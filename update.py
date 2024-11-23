# po_processor_app.py

import os
from pathlib import Path
import pandas as pd
import shutil
from datetime import datetime, timedelta
import sqlite3
from llama_parse import LlamaParse
from database_utils import insert_csv_to_db
import streamlit as st
import tempfile
import json

# Set page configuration
st.set_page_config(
    page_title="PO Processing System",
    page_icon="📋",
    layout="wide"
)

# Custom CSS for elegant styling
st.markdown("""
    <style>
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
        }
        .st-emotion-cache-1v0mbdj {
            width: 100%;
        }
        .dataframe {
            font-size: 12px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_df' not in st.session_state:
    st.session_state.processed_df = None

# Set API key
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-svCPu1UniVECsxWEeQINhixGgBZgSHjr4OcIp0o1VX57JMsm"

# Original functions from po_pdf.py
def save_pages_to_files(documents_with_instruction, base_filename="po_", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    
    for page_num in range(len(documents_with_instruction)):
        try:
            file_name = f"{base_filename}{page_num + 1}.md"
            file_path = os.path.join(output_dir, file_name)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(documents_with_instruction[page_num].text)
            
            st.write(f"Successfully saved page {page_num + 1}")
            
        except AttributeError:
            st.warning(f"Warning: Page {page_num + 1} has no text attribute")
        except Exception as e:
            st.error(f"Error saving page {page_num + 1}: {str(e)}")

# def convert_md_to_df(input_folder, output_folder):
#     Path(output_folder).mkdir(parents=True, exist_ok=True)
#     md_files = [f for f in os.listdir(input_folder) if f.endswith('.md')]
    
#     for md_file in md_files:
#         try:
#             file_path = os.path.join(input_folder, md_file)
#             df = pd.read_table(
#                 file_path,
#                 sep='|',
#                 engine='python',
#                 dtype=str
#             )
            
#             df.columns = df.columns.str.strip().str.replace('-', '')
#             df = df.astype(str)
#             df = df[~df.iloc[:, 0].str.contains(r'^-+$', na=False)]
#             df = df.apply(lambda x: x.str.strip())
            
#             numeric_columns = ['Quantity', 'Price', 'Total', 'SizeXS', 'SizeS', 'SizeM',
#                              'SizeL', 'SizeXL', 'SizeXXL']
            
#             for col in numeric_columns:
#                 if col in df.columns:
#                     df[col] = df[col].str.replace(',', '')
#                     df[col] = pd.to_numeric(df[col], errors='coerce')
            
#             output_filename = os.path.splitext(md_file)[0] + '.csv'
#             output_path = os.path.join(output_folder, output_filename)
#             df.to_csv(output_path, index=False)
#             st.write(f"Successfully converted {md_file} to CSV")
            
#         except Exception as e:
#             st.error(f"Error processing {md_file}: {str(e)}")
#             st.write(f"Detailed error: {traceback.format_exc()}")

def convert_md_to_df(input_folder, output_folder):
    """
    Convert markdown files from input folder to pandas DataFrames and save them as CSV files
    in the output folder. Handles both markdown table and JSON formats.

    Parameters:
    input_folder (str): Path to the folder containing markdown files
    output_folder (str): Path to the folder where CSV files will be saved
    """
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Get all markdown files from input folder
    md_files = [f for f in os.listdir(input_folder) if f.endswith('.md')]

    for md_file in md_files:
        file_path = os.path.join(input_folder, md_file)

        try:
            # Try reading the file as a markdown table
            df = pd.read_table(
                file_path,
                sep='|',  # Tables in markdown use | as separator
                engine='python',
                dtype=str  # Read all columns as strings initially
            )

            # Clean the DataFrame (as previously)
            df.columns = df.columns.str.strip().str.replace('-', '')
            df = df.astype(str)
            df = df[~df.iloc[:, 0].str.contains(r'^-+$', na=False)]
            df = df.apply(lambda x: x.str.strip())

            # Convert numeric columns back to appropriate types
            numeric_columns = ['Quantity', 'Price', 'Total', 'SizeXS', 'SizeS', 'SizeM',
                               'SizeL', 'SizeXL', 'SizeXXL']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].str.replace(',', '')
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            output_filename = os.path.splitext(md_file)[0] + '.csv'
            output_path = os.path.join(output_folder, output_filename)
            df.to_csv(output_path, index=False)
            print(f"Successfully converted {md_file} to {output_filename}")

        except pd.errors.ParserError as e:
            print(f"Markdown table parsing failed for {md_file}, attempting JSON parsing.")

            try:
                # Read the JSON file and remove the first and last lines
                with open(file_path, 'r', encoding='utf-8') as file:
                    json_data = file.readlines()

                if not json_data:
                    raise ValueError(f"File {file_path} is empty.")

                # Remove first and last lines
                modified_data = json_data[1:-1]

                # Save the modified JSON back to a file
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.writelines(modified_data)

                # Load the modified JSON into a DataFrame
                df = pd.read_json(file_path, lines=False)

                # Save JSON DataFrame to CSV
                output_filename = os.path.splitext(md_file)[0] + '.csv'
                output_path = os.path.join(output_folder, output_filename)
                df.to_csv(output_path, index=False)
                print(f"Successfully converted JSON in {md_file} to {output_filename}")

            except ValueError as ve:
                print(f"Error processing {md_file}: {str(ve)}")
            except json.JSONDecodeError as json_error:
                print(f"Failed to process {md_file} as JSON. Error: {str(json_error)}")
            except Exception as json_general_error:
                print(f"An unexpected error occurred for {md_file}. Error: {str(json_general_error)}")

        except Exception as e:
            print(f"Error processing {md_file}: {str(e)}")
            import traceback
            print(traceback.format_exc())


def merge_csv_files(input_file, output_file):
    """
    Merge all CSV files in the input folder into a single DataFrame and save it as a CSV file.

    Parameters:
    input_folder (str): Path to the folder containing CSV files
    output_file (str): Path where the merged CSV file will be saved

    Returns:
    pd.DataFrame: The merged DataFrame
    """
    # Get all CSV files from input folder
    csv_files = [f for f in os.listdir(input_file) if f.endswith('.csv')]

    if not csv_files:
        raise ValueError(f"No CSV files found in {input_file}")

    # Initialize an empty list to store DataFrames
    dfs = []

    # Read each CSV file
    for csv_file in csv_files:
        file_path = os.path.join(input_file, csv_file)
        try:
            # Read CSV with proper data types
            df = pd.read_csv(file_path)

            # Convert numeric columns to appropriate types
            numeric_columns = ['Quantity', 'Price', 'Total', 'SizeXS', 'SizeS', 'SizeM',
                             'SizeL', 'SizeXL', 'SizeXXL']

            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Add source file name as a column (optional)
            df['SourceFile'] = csv_file

            dfs.append(df)
            print(f"Successfully read {csv_file}")

        except Exception as e:
            print(f"Error processing {csv_file}: {str(e)}")

    # Combine all DataFrames
    if dfs:
        merged_df = pd.concat(dfs, ignore_index=True)

        # Reorder columns to a logical sequence
        column_order = [
            'OrderNumber', 'StyleCode', 'Description', 'ColorCode', 'ColorName',
            'Quantity', 'Price', 'Total', 'Fabric', 'Composition',
            'SizeXS', 'SizeS', 'SizeM', 'SizeL', 'SizeXL', 'SizeXXL',
            'IssueDate', 'PickupDate', 'OwnershipDate', 'Season',
            'SourceFile'
        ]

        # Only include columns that actually exist in the DataFrame
        final_columns = [col for col in column_order if col in merged_df.columns]
        # Add any columns that exist in the DataFrame but weren't in our predefined order
        remaining_columns = [col for col in merged_df.columns if col not in final_columns]
        final_columns.extend(remaining_columns)

        merged_df = merged_df[final_columns]

        #changing Dataframe as per logic flow
        merged_df = merged_df[~merged_df.apply(lambda row: row.astype(str).str.contains('---').any(), axis=1)]
        merged_df['Line'] = pd.to_numeric(merged_df['Line'])
        merged_df.sort_values(by='Line', ascending=True, inplace=True)
        merged_df.reset_index(drop=True, inplace=True)

        # Assuming merged_df is your DataFrame
        first_issue_date = merged_df['IssueDate'].iloc[0]  # Get the date from the first row
        first_pickup_date = merged_df['PickupDate'].iloc[0]
        first_ownership_date = merged_df['OwnershipDate'].iloc[0]
        first_season_date = merged_df['Season'].iloc[0]
        first_order_number = merged_df['OrderNumber'].iloc[0]

        merged_df['IssueDate'] = first_issue_date
        merged_df['PickupDate'] = first_pickup_date
        merged_df['OwnershipDate'] = first_ownership_date
        merged_df['Season'] = first_season_date
        merged_df['OrderNumber'] = first_order_number

        #merged_df.drop(columns=['SourceFile', 'Unnamed: 0','Unnamed: 22'], inplace=True)
        # Columns to check and drop
        columns_to_drop = ['SourceFile', 'Unnamed: 0', 'Unnamed: 22']

        # Check if columns exist in the DataFrame
        columns_in_df = [col for col in columns_to_drop if col in merged_df.columns]

        # Drop the columns if they exist
        if columns_in_df:
            merged_df.drop(columns=columns_in_df, inplace=True)
        merged_df = merged_df.dropna(subset=['StyleCode', 'Line'], how='all')

        # Save the merged DataFrame
        merged_df.to_csv(output_file, index=False)
        print(f"\nSuccessfully merged {len(dfs)} files into {output_file}")
        print(f"Total rows: {len(merged_df)}")

        # Display some basic statistics
        print("\nQuick Summary:")
        print(f"Total unique StyleCodes: {merged_df['StyleCode'].nunique()}")
        print(f"Total unique Colors: {merged_df['ColorName'].nunique()}")
        print(f"Total Quantity: {merged_df['Quantity'].sum():,.0f}")
        print(f"Total Value: ${merged_df['Total'].sum():,.2f}")

        return merged_df
    else:
        raise ValueError("No DataFrames to merge!")

def empty_folders(*folder_paths):
    for folder_path in folder_paths:
        if os.path.exists(folder_path):
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    st.error(f"Failed to delete {item_path}: {e}")
            #st.write(f"Emptied folder: {folder_path}")
        else:
            st.warning(f"Folder does not exist: {folder_path}")

def process_uploaded_file(uploaded_file, input_folder, output_folder, merged_folder):
    """Process the uploaded PDF file"""
    if uploaded_file is None:
        return None

    # Save uploaded file temporarily
    temp_pdf_path = os.path.join(input_folder, "uploaded_po.pdf")
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    with st.spinner("Processing PDF..."):
        # Parse PDF
        documents_with_instruction = LlamaParse(
            result_type="markdown",
            parsing_instruction="""
            This document is a Garment Purchase Order (PO), issued by the buyer to the garment supplier, specifying essential order details such as style, quantity, size breakdown, color, price, delivery date, and payment terms also Total amount. It serves as a contract between the buyer and supplier.

            Extract and consolidate the required data with out any Notes: details. If any value for a required column is missing, check subsequent pages to ensure completeness.

            Required columns:
                expected_columns = [
                    'Line', 'StyleCode', 'Description', 'ColorCode', 'ColorName', 'Quantity',
                    'Price', 'Total', 'Fabric', 'Composition', 'SizeXS', 'SizeS', 'SizeM',
                    'SizeL', 'SizeXL', 'SizeXXL', 'IssueDate', 'PickupDate', 'OwnershipDate',
                    'Season', 'OrderNumber'
                ]
            """
        ).load_data(temp_pdf_path)

        # Save pages
        save_pages_to_files(documents_with_instruction, base_filename="po_", output_dir=input_folder)

        # Convert to CSV
        convert_md_to_df(input_folder, output_folder)

        # Create merged output filename
        current_date = datetime.now().strftime("%Y-%m-%d")
        output_file = os.path.join(merged_folder, f"po_{current_date}.csv")

        # Merge CSV files and get DataFrame
        merged_df = merge_csv_files(output_folder, output_file)

        return merged_df

# def main():
#     st.title("📋 PO Processing System")
#     st.write("Upload a PO PDF file to process and manage the data")

#     # Clear session state on new file upload
#     if 'uploaded_file' not in st.session_state:
#         st.session_state['uploaded_file'] = None
#         st.session_state['processed_df'] = None

#     # File uploader
#     uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

#     # Reset session state when a new file is uploaded
#     if uploaded_file and uploaded_file != st.session_state['uploaded_file']:
#         st.session_state['uploaded_file'] = uploaded_file
#         st.session_state['processed_df'] = None

#     if uploaded_file is not None:
#         # Create temporary directories
#         temp_dir = tempfile.mkdtemp()
#         input_folder = os.path.join(temp_dir, "output")
#         output_folder = os.path.join(temp_dir, "converted_files")
#         merged_folder = os.path.join(temp_dir, "merged_output")

#         os.makedirs(input_folder, exist_ok=True)
#         os.makedirs(output_folder, exist_ok=True)
#         os.makedirs(merged_folder, exist_ok=True)

#         try:
#             # Process the file and update the processed_df if it's a new file
#             if st.session_state['processed_df'] is None:
#                 st.session_state['processed_df'] = process_uploaded_file(
#                     uploaded_file, input_folder, output_folder, merged_folder
#                 )

#             if st.session_state['processed_df'] is not None:
#                 st.success("File processed successfully!")

#                 # Display summary statistics
#                 col1, col2, col3, col4 = st.columns(4)
#                 with col1:
#                     st.metric("Total Styles", st.session_state['processed_df']['StyleCode'].nunique())
#                 with col2:
#                     st.metric("Total Colors", st.session_state['processed_df']['ColorName'].nunique())
#                 with col3:
#                     st.metric("Total Quantity", f"{st.session_state['processed_df']['Quantity'].sum():,.0f}")
#                 with col4:
#                     st.metric("Total Value", f"${st.session_state['processed_df']['Total'].sum():,.2f}")

#                 # Data Editor
#                 st.subheader("Edit Data")
#                 edited_df = st.data_editor(
#                     st.session_state['processed_df'],
#                     num_rows="dynamic",
#                     use_container_width=True
#                 )

#                 # Database Operations
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     if st.button("Save to Database", type="primary"):
#                         try:
#                             # Save edited DataFrame to temporary CSV
#                             temp_csv = os.path.join(merged_folder, "edited_po.csv")
#                             edited_df.to_csv(temp_csv, index=False)

#                             # Insert into database
#                             insert_csv_to_db("garment_orders.db", temp_csv)
#                             st.success("Data successfully saved to database!")
#                         except Exception as e:
#                             st.error(f"Error saving to database: {str(e)}")

#                 with col2:
#                     if st.button("Download CSV"):
#                         # Convert DataFrame to CSV
#                         csv = edited_df.to_csv(index=False)
#                         st.download_button(
#                             label="Click to Download",
#                             data=csv,
#                             file_name="processed_po.csv",
#                             mime="text/csv"
#                         )

#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")

#         finally:
#             # Cleanup temporary directories
#             shutil.rmtree(temp_dir)
            

def main():
    st.title("📋 PO Processing System")
    st.write("Upload a PO PDF file to process and manage the data")

    # Database file path
    db_file = "garment_orders.db"

    # Clear session state on new file upload
    if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = None
        st.session_state['processed_df'] = None

    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

    # Reset session state when a new file is uploaded
    if uploaded_file and uploaded_file != st.session_state['uploaded_file']:
        st.session_state['uploaded_file'] = uploaded_file
        st.session_state['processed_df'] = None

    # Enhanced Search Section
    st.subheader("🔍 Search Orders")
    
    # Create tabs for different search modes
    search_tab, advanced_tab = st.tabs(["Quick Search", "Advanced Search"])
    
    with search_tab:
        with st.form("quick_search_form"):
            search_term = st.text_input("Search by Order Number, Style Code, or Color Name")
            quick_search = st.form_submit_button("Quick Search")
            
        if quick_search and search_term:
            try:
                with sqlite3.connect(db_file) as conn:
                    query = """
                    SELECT * FROM orders
                    WHERE OrderNumber LIKE ?
                    OR StyleCode LIKE ?
                    OR ColorName LIKE ?
                    """
                    search_pattern = f"%{search_term}%"
                    params = (search_pattern, search_pattern, search_pattern)
                    results = pd.read_sql_query(query, conn, params=params)
                    display_search_results(results)
            except Exception as e:
                st.error(f"Search error: {str(e)}")

    with advanced_tab:
        with st.form("advanced_search_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                order_number = st.text_input("Order Number")
                style_code = st.text_input("Style Code")
                
            with col2:
                color_name = st.text_input("Color Name")
                min_quantity = st.number_input("Minimum Quantity", min_value=0)
                
            with col3:
                date_range = st.date_input(
                    "Date Range",
                    value=(datetime.now().date() - timedelta(days=30), datetime.now().date()),
                    max_value=datetime.now().date()
                )
                
            sort_by = st.selectbox(
                "Sort By",
                options=["IssueDate", "OrderNumber", "StyleCode", "Quantity", "Total"],
                index=0
            )
            sort_order = st.radio("Sort Order", ["Ascending", "Descending"], horizontal=True)
            
            advanced_search = st.form_submit_button("Search")
            
        if advanced_search:
            try:
                with sqlite3.connect(db_file) as conn:
                    conditions = []
                    params = []
                    
                    if order_number:
                        conditions.append("OrderNumber LIKE ?")
                        params.append(f"%{order_number}%")
                    
                    if style_code:
                        conditions.append("StyleCode LIKE ?")
                        params.append(f"%{style_code}%")
                    
                    if color_name:
                        conditions.append("ColorName LIKE ?")
                        params.append(f"%{color_name}%")
                    
                    if min_quantity > 0:
                        conditions.append("Quantity >= ?")
                        params.append(min_quantity)
                    
                    if len(date_range) == 2:
                        conditions.append("IssueDate BETWEEN ? AND ?")
                        params.extend([date_range[0], date_range[1]])
                    
                    where_clause = " AND ".join(conditions) if conditions else "1=1"
                    order_direction = "DESC" if sort_order == "Descending" else "ASC"
                    
                    query = f"""
                    SELECT * FROM orders
                    WHERE {where_clause}
                    ORDER BY {sort_by} {order_direction}
                    """
                    
                    results = pd.read_sql_query(query, conn, params=params)
                    display_search_results(results)
                    
            except Exception as e:
                st.error(f"Advanced search error: {str(e)}")

    # File Processing Section
    if uploaded_file is not None:
        # Create temporary directories
        temp_dir = tempfile.mkdtemp()
        input_folder = os.path.join(temp_dir, "output")
        output_folder = os.path.join(temp_dir, "converted_files")
        merged_folder = os.path.join(temp_dir, "merged_output")

        os.makedirs(input_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(merged_folder, exist_ok=True)

        try:
            # Process the file and update the processed_df if it's a new file
            if st.session_state['processed_df'] is None:
                st.session_state['processed_df'] = process_uploaded_file(
                    uploaded_file, input_folder, output_folder, merged_folder
                )

            if st.session_state['processed_df'] is not None:
                st.success("File processed successfully!")

                # Display summary statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Styles", st.session_state['processed_df']['StyleCode'].nunique())
                with col2:
                    st.metric("Total Colors", st.session_state['processed_df']['ColorName'].nunique())
                with col3:
                    st.metric("Total Quantity", f"{st.session_state['processed_df']['Quantity'].sum():,.0f}")
                with col4:
                    st.metric("Total Value", f"${st.session_state['processed_df']['Total'].sum():,.2f}")

                # Data Editor
                st.subheader("Edit Data")
                edited_df = st.data_editor(
                    st.session_state['processed_df'],
                    num_rows="dynamic",
                    use_container_width=True
                )

                # Database Operations
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save to Database", type="primary"):
                        try:
                            # Save edited DataFrame to temporary CSV
                            temp_csv = os.path.join(merged_folder, "edited_po.csv")
                            edited_df.to_csv(temp_csv, index=False)

                            # Insert into database
                            insert_csv_to_db(db_file, temp_csv)
                            st.success("Data successfully saved to database!")
                        except Exception as e:
                            st.error(f"Error saving to database: {str(e)}")

                with col2:
                    if st.button("Download CSV"):
                        # Convert DataFrame to CSV
                        csv = edited_df.to_csv(index=False)
                        st.download_button(
                            label="Click to Download",
                            data=csv,
                            file_name="processed_po.csv",
                            mime="text/csv"
                        )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

        finally:
            # Cleanup temporary directories
            shutil.rmtree(temp_dir)

def display_search_results(results):
    """Display search results with statistics and export options"""
    if not results.empty:
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Results Found", len(results))
        with col2:
            st.metric("Total Styles", results['StyleCode'].nunique())
        with col3:
            st.metric("Total Quantity", f"{results['Quantity'].sum():,.0f}")
        with col4:
            st.metric("Total Value", f"${results['Total'].sum():,.2f}")
        
        # Display results in an interactive table
        st.dataframe(
            results,
            use_container_width=True,
            column_config={
                "Total": st.column_config.NumberColumn(
                    "Total",
                    format="$%.2f"
                ),
                "Quantity": st.column_config.NumberColumn(
                    "Quantity",
                    format="%d"
                ),
                "IssueDate": st.column_config.DateColumn(
                    "Issue Date",
                    format="YYYY-MM-DD"
                )
            }
        )
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            csv = results.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="search_results.csv",
                mime="text/csv"
            )
        
        with col2:
            excel_buffer = io.BytesIO()
            results.to_excel(excel_buffer, index=False)
            excel_data = excel_buffer.getvalue()
            st.download_button(
                label="Download Results as Excel",
                data=excel_data,
                file_name="search_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("No results found matching your search criteria.")

if __name__ == "__main__":
    main()

