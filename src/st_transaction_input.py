from idlelib.pyparse import trans

import streamlit as st
from src.adding_transaction import AddingTransaction
import src.utils as utils
from collections import defaultdict
import datetime




def transaction_input_tab(db_manager):

    edit_column,_, list_column = st.columns([0.59,0.01,0.4])
    list_column = list_column.container(border=True)
    with list_column:
        st.markdown("## Existing Transactions")

        if "transaction_viewer_date" not in st.session_state:
            st.session_state["transaction_viewer_date"] = {"depth": "years", "timestamp": None, "transaction_id": None}

        def click_button(new_depth, new_timestamp=None, transaction_id=None):
            st.session_state["transaction_viewer_date"]["depth"] = new_depth
            if new_timestamp is not None:
                st.session_state["transaction_viewer_date"]["timestamp"] = new_timestamp
            if transaction_id is not None:
                st.session_state["transaction_viewer_date"]["transaction_id"] = transaction_id

        def move_depth(depth, diff=0):
            next_depths = [
                "years",
                "months",
                "days",
                "transactions",
                "specific"
            ]
            return next_depths[
                (next_depths.index(depth)+diff)%len(next_depths)
            ]

        state = st.session_state["transaction_viewer_date"]
        current, increase  = st.columns([1,1])
        increase.button(
            "Previous", icon="⬆️",
            use_container_width=True,
            disabled=state["depth"]=="years",
            on_click=click_button,
            args=(move_depth(state["depth"], -1),)
        )
        if state["depth"] == "years":
            current.write(f"### Years")
        elif state["depth"] == "months":
            current.write(f"### Months of {state['timestamp'].year}")
        elif state["depth"] == "days":
            current.write(f"### Days in {state['timestamp'].strftime('%b %Y')}")
        elif state["depth"] == "transactions":
            current.write(f"### {state['timestamp'].strftime('%a %d %b %y')}")
        elif state["depth"] == "specific":
            current.write(f"### Transaction ID {state['transaction_id']}")

        # st.divider()
        transactions_info = get_transactions_info(db_manager, state)

        if state["depth"] == "transactions":
            for id_ in transactions_info:
                st.button(
                    transactions_info[id_],
                    use_container_width=True,
                    on_click=click_button,
                    args=("specific", None, id_)
                )
        elif state["depth"] == "specific":
            st.metric("Vendor", transactions_info["vendor"])
            if not utils.isNone(transactions_info["shop_location"]):
                st.metric("Location", transactions_info["shop_location"])
            cols = st.columns([1,1.5])
            cols[0].metric("Money", transactions_info["money_string"])
            cols[1].metric("Money Store", transactions_info["money_store"])
            if not utils.isNone(transactions_info["category_string"]):
                st.metric("Category", transactions_info["category_string"])
            cols = st.columns([1.2,1])
            cols[0].metric("Date", transactions_info["date"])
            if not utils.isNone(transactions_info["time"]):
                cols[1].metric("Time", transactions_info["time"])

            cols = st.columns([1,1])
            if cols[0].button("Edit", use_container_width=True, icon="✏️"):
                pass
            if cols[1].button("Delete", use_container_width=True, icon="🗑️"):
                db_manager.db.delete("Transactions", "transaction_id", state["transaction_id"])
                click_button("days")

        else:
            for date in transactions_info:
                st.button(
                    f"{date}   ->  Income: £{transactions_info[date]['income']:.2f}   Spending: £{transactions_info[date]['spending']:.2f}",
                    use_container_width=True,
                    on_click=click_button,
                    args=(
                        move_depth(state["depth"], 1),
                        transactions_info[date]["timestamp"])
                )


    with edit_column:
        st.markdown("## Add Transaction")
        left_input, right_input = st.columns(2)
        adding_spending = AddingTransaction(st.session_state, db_manager)

        adding_spending.set_vendor_name(
            left_input.selectbox("Vendor Name", db_manager.get_all_vendor_names(),
                                      accept_new_options=True, index=None)
        )
        selected_shop_locations = db_manager.get_shop_locations(adding_spending.vendor_name)
        adding_spending.set_shop_location(
            right_input.selectbox("Location Name", selected_shop_locations, accept_new_options=True,
                                      index=None)
        )

        adding_spending.set_spending_category(
            left_input.selectbox("Spending Category", db_manager.get_all_categories(), index=None)
        )
        adding_spending.set_money_store_used(
            right_input.selectbox("Money Store Used", db_manager.get_all_money_stores(), index=None)
        )
        adding_spending.set_spending_date(
            left_input.date_input("Spending Date", format="DD/MM/YYYY")
        )
        adding_spending.set_spending_time(
            right_input.time_input("Spending Time", value=None)
        )

        adding_spending.set_override_money(
            left_input.number_input("Money Transferred", value=None)
        )
        adding_spending.set_is_income(
            right_input.selectbox("Spending or Income", ["Spending", "Income"])
        )

        if adding_spending.override_money is not None:
            total_cost = adding_spending.override_money
        else:
            total_cost = 0
        if not adding_spending.is_income:
            st.markdown("## Items")

            if "product_selection" not in st.session_state:
                st.session_state["product_selection"] = None

            selected_product = st.selectbox(
                "Add Item",
                options=db_manager.get_all_products(adding_spending.vendor_name),
                accept_new_options=True, index=None, key="product_selection"
            )

            def add_item_button_press(adding_spending_obj, selected_option):
                adding_spending_obj.add_product(selected_option)
                del st.session_state["product_selection"]

            st.button("Add Item",
                      on_click=lambda: add_item_button_press(adding_spending, selected_product))

            spending_display_df = adding_spending.to_display_df()

            st.session_state["adding_spending_df"] = adding_spending.from_display_df(
                utils.data_editor(
                    spending_display_df,
                    {
                        "ID": {"type": "number", "editable": False},
                        "Price Per": {"type": "number", "format": "£%.2f"},
                    }
                )
            )

            total_cost = sum(filter(
                lambda num: not utils.isNone(num),
                spending_display_df["Price Per"] * spending_display_df["Num Purchased"]
            ))
            st.divider()
            st.markdown(f"Add Transaction of spending £{total_cost:.2f}")
        else:
            st.divider()
            st.markdown(f"Add Income of £{total_cost:.2f}")
        if st.button("Add Transaction"):
            adding_spending.add_transaction_to_db()
            del st.session_state["adding_spending_df"]
            st.toast("Transaction Added!")

def get_transactions_info(db_manager, state):
    transactions_df = db_manager.transactions.db_data
    transactions_dict = dict(zip(
        transactions_df["transaction_id"],
        transactions_df["date"].apply(utils.string_to_date)
    ))
    output = {}
    if state["depth"] == "years":
        years = defaultdict(list)
        for id_ in transactions_dict:
            years[transactions_dict[id_].year].append(id_)
        for year in years:
            timestamp = datetime.date(year=year, month=1, day=1)
            output[timestamp.strftime("%Y")] = summarise_transactions(
                db_manager,
                transactions_df[transactions_df["transaction_id"].isin(years[year])],
                timestamp
            )
    elif state["depth"] == "months":
        months = defaultdict(list)
        for id_ in transactions_dict:
            if state["timestamp"].year == transactions_dict[id_].year:
                months[transactions_dict[id_].month].append(id_)
        for month in months:
            timestamp = datetime.date(year=state["timestamp"].year, month=month,day=1)
            output[
                timestamp.strftime("%B")
            ] = summarise_transactions(
                db_manager,
                transactions_df[transactions_df["transaction_id"].isin(months[month])],
                timestamp
            )
    elif state["depth"] == "days":
        days = defaultdict(list)
        for id_ in transactions_dict:
            if state["timestamp"].year == transactions_dict[id_].year and state["timestamp"].month == transactions_dict[id_].month:
                days[transactions_dict[id_].day].append(id_)
        for day in days:
            timestamp = datetime.date(year=state["timestamp"].year, month=state["timestamp"].month,day=day)
            output[
                timestamp.strftime("%d %a")
            ] = summarise_transactions(
                db_manager,
                transactions_df[transactions_df["transaction_id"].isin(days[day])],
                timestamp
            )
    elif state["depth"] == "transactions":
        transactions = []
        for id_ in transactions_dict:
            if state["timestamp"] == transactions_dict[id_]:
                transactions.append(id_)
        for transaction_id in transactions:
            row = db_manager.transactions.get_filtered_df("transaction_id", transaction_id)
            summary = summarise_transactions(db_manager, row)
            row = row.iloc[0]
            if summary["income"]>0:
                output[transaction_id] = f"{row['vendor_name']} -> +£{summary['income']:.2f}"
            else:
                output[transaction_id] = f"{row['vendor_name']} -> -£{summary['spending']:.2f}"
    elif state["depth"] == "specific":
        row = db_manager.transactions.get_db_row(state["transaction_id"])

        return {
            "date": row["date"],
            "time": row["time"],
            "vendor": row["vendor_name"],
            "shop_location": row["shop_location"],
            "money_string": f"{'+' if row['is_income'] else '-'}£{find_transaction_value(db_manager, row):.2f}",
            "money_store": row["money_store"],
            "category_string": row["category_string"]
        }
    return output

def summarise_transactions(db_manager, transactions_df, timestamp=None):
    transactions_df = transactions_df.copy()
    transactions_df["money_moved"] =  transactions_df.apply(
        lambda row:
        find_transaction_value(db_manager, row),
        axis=1
    )

    return {
        "income": sum(transactions_df[transactions_df["is_income"]==True]["money_moved"]),
        "spending": sum(transactions_df[transactions_df["is_income"]==False]["money_moved"]),
        "timestamp": timestamp,
    }

def find_transaction_value(db_manager, df_row) -> float:
    if not utils.isNone(df_row["override_money"]):
        return df_row["override_money"]
    else:
        return sum(db_manager.spending_items.get_filtered_df("transaction_id")["display_price"])
