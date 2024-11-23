# 📋 Llama Parser with Streamlit UI for PDF Data Management

This project provides a streamlined solution for parsing PDF files using **LlamaParser**, allowing users to visualize, edit, and save the parsed data through an intuitive **Streamlit** interface. The final processed data can be saved to an **SQLite** database for further use.

---

## 🎯 Features

1. **PDF Parsing**: Automatically extracts tabular data and key details from PDF files using LlamaParser.
2. **Streamlit Interface**:
   - Upload PDF files for parsing.
   - View the parsed data in an editable table.
   - Perform real-time edits through the interface.
3. **Data Persistence**:
   - Save the edited data into an **SQLite database**.
   - Option to download the processed data as a CSV file.

---

## 🛠️ Technology Stack

- **Python**: Core programming language for processing and data management.
- **LlamaParser**: For extracting structured data from PDF files.
- **Streamlit**: Interactive web application framework for creating a user-friendly interface.
- **SQLite**: Lightweight relational database for storing processed data.

---

## 🚀 How It Works

1. **Upload PDF**: Users can upload a PDF file through the Streamlit web interface.
2. **Parse PDF Data**: The LlamaParser processes the PDF and extracts the data into a structured format (e.g., JSON or DataFrame).
3. **View and Edit Data**:
   - The parsed data is displayed in an editable table within the Streamlit interface.
   - Users can make changes directly in the interface.
4. **Save or Download**:
   - Save the edited data to an SQLite database for storage and analysis.
   - Optionally, download the data as a CSV file for local use.

---

## 🧰 Prerequisites

1. **Python 3.8+**
2. Install required libraries:
   ```bash
   pip install streamlit pandas sqlite3 llama-index
   ```

---

## 🔧 Installation and Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/basudabC/AI-Pdf-Parser-to-Database-Insert.git
   cd llama-parser-streamlit
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Open your browser and go to the local Streamlit app URL (usually `http://localhost:8501`).

---

## 📋 Sample Workflow

1. **Upload a PDF**:
   - Use the file uploader in the Streamlit app to upload your PDF.
   
2. **Edit Data**:
   - View the parsed data in a table.
   - Make changes directly through the table editor.

3. **Save to Database**:
   - Click on the "Save to Database" button to persist the edited data into the SQLite database.

4. **Download CSV**:
   - Optionally, click the "Download CSV" button to download the processed data.

---

## 🗂️ Project Structure

```
├── app.py                 # Main application script
├── requirements.txt       # Python dependencies
├── utils/
│   ├── parser.py          # LlamaParser integration
│   ├── db_operations.py   # SQLite database interactions
│   ├── file_utils.py      # Temporary file handling
├── templates/             # HTML templates for the Streamlit app
└── README.md              # Project documentation
```

---

## 🛡️ License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---

## 📧 Contact

For any questions or suggestions, feel free to reach out via [your email or GitHub profile](https://github.com/your-username).

---

Enjoy seamless PDF data parsing and management with **LlamaParser + Streamlit**! 🌟
