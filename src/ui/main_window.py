# src/ui/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QScrollArea, QDialog,
    QListWidget, QListWidgetItem, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from models.prompt import PromptTemplate
from utils.database import Database
from datetime import datetime

# Dark mode option
DARK_MODE_STYLESHEET = """
    QMainWindow, QWidget, QDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QLabel, QPushButton, QTextEdit, QListWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QPushButton {
        background-color: #333333;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px;
    }
    QPushButton:hover {
        background-color: #444444;
    }
    QTextEdit, QListWidget {
        border: 1px solid #555555;
    }
"""

class PromptHistoryDialog(QDialog):
    """Dialog window to display and manage saved prompts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.parent_window = parent
        self.setWindowTitle("Saved Prompts")
        self.setGeometry(150, 150, 900, 600)
        self.init_ui()
        self.load_prompts()
        
    
    def init_ui(self):
        """Initialize UI for the dialog"""
        main_layout = QVBoxLayout()
        
        # Top section: Filter buttons
        filter_layout = QHBoxLayout()
        
        all_button = QPushButton("All Prompts")
        all_button.clicked.connect(self.show_all)
        
        templates_button = QPushButton("Templates")
        templates_button.clicked.connect(self.show_templates)
        
        favorites_button = QPushButton("Favorites ★")
        favorites_button.clicked.connect(self.show_favorites)
        
        filter_layout.addWidget(all_button)
        filter_layout.addWidget(templates_button)
        filter_layout.addWidget(favorites_button)
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QTextEdit()
        self.search_input.setMaximumHeight(35)
        self.search_input.setPlaceholderText("Search by title, content, or tags...")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_prompts)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        
        main_layout.addLayout(search_layout)
        
        # Prompts list
        list_label = QLabel("Saved Prompts:")
        label_font = QFont()
        label_font.setBold(True)
        list_label.setFont(label_font)
        
        self.prompts_list = QListWidget()
        self.prompts_list.itemClicked.connect(self.on_prompt_selected)
        
        main_layout.addWidget(list_label)
        main_layout.addWidget(self.prompts_list)
        
        # Display area for selected prompt
        details_label = QLabel("Prompt Details:")
        details_label.setFont(label_font)
        
        self.details_display = QTextEdit()
        self.details_display.setReadOnly(True)
        self.details_display.setMinimumHeight(200)
        
        main_layout.addWidget(details_label)
        main_layout.addWidget(self.details_display)
        
        # Button section
        button_layout = QHBoxLayout()
        
        
        load_button = QPushButton("Load Selected Prompt")
        load_button.clicked.connect(self.load_selected_prompt)
        load_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_selected_prompt)
        delete_button.setStyleSheet("background-color: #f44336; color: white;")
        
        toggle_favorite_button = QPushButton("Toggle Favorite ★")
        toggle_favorite_button.clicked.connect(self.toggle_favorite)
        toggle_favorite_button.setStyleSheet("background-color: #FF9800; color: white;")
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(load_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(toggle_favorite_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
   
    def load_prompts(self):
        """Load all prompts into the list"""
        self.prompts_list.clear()
        prompts = self.db.get_all_prompts(include_templates=True)
        
        for prompt in prompts:
            # Create list item with title or identifier
            display_text = prompt.title if prompt.title else f"Prompt {prompt.id}"
            
            # Add indicator for templates and favorites
            indicators = ""
            if prompt.is_template:
                indicators += " [TEMPLATE]"
            if prompt.is_favorite:
                indicators += " ★"
            
            item = QListWidgetItem(display_text + indicators)
            item.setData(Qt.UserRole, prompt.id)  # Store prompt ID
            self.prompts_list.addItem(item)
    
    def show_all(self):
        """Show all prompts"""
        self.load_prompts()
    
    def show_templates(self):
        """Show only templates"""
        self.prompts_list.clear()
        templates = self.db.get_templates()
        
        for template in templates:
            display_text = template.title if template.title else f"Template {template.id}"
            if template.is_favorite:
                display_text += " ★"
            
            item = QListWidgetItem(display_text + " [TEMPLATE]")
            item.setData(Qt.UserRole, template.id)
            self.prompts_list.addItem(item)
    
    def show_favorites(self):
        """Show only favorite prompts"""
        self.prompts_list.clear()
        favorites = self.db.get_favorites()
        
        for favorite in favorites:
            display_text = favorite.title if favorite.title else f"Prompt {favorite.id}"
            if favorite.is_template:
                display_text += " [TEMPLATE]"
            
            item = QListWidgetItem(display_text + " ★")
            item.setData(Qt.UserRole, favorite.id)
            self.prompts_list.addItem(item)
    
    def search_prompts(self):
        """Search prompts based on input"""
        search_term = self.search_input.toPlainText().strip()
        
        if not search_term:
            self.load_prompts()
            return
        
        self.prompts_list.clear()
        results = self.db.search_prompts(search_term)
        
        if not results:
            QMessageBox.information(self, "Search Results", 
                                   f"No prompts found matching '{search_term}'")
            self.load_prompts()
            return
        
        for prompt in results:
            display_text = prompt.title if prompt.title else f"Prompt {prompt.id}"
            
            indicators = ""
            if prompt.is_template:
                indicators += " [TEMPLATE]"
            if prompt.is_favorite:
                indicators += " ★"
            
            item = QListWidgetItem(display_text + indicators)
            item.setData(Qt.UserRole, prompt.id)
            self.prompts_list.addItem(item)
    
    def on_prompt_selected(self, item):
        """Display details of selected prompt"""
        prompt_id = item.data(Qt.UserRole)
        prompt = self.db.get_prompt(prompt_id)
        
        if not prompt:
            return
        
        # Format the display
        details = f"""
═══════════════════════════════════════════════════════════════

TITLE: {prompt.title if prompt.title else "Untitled"}

Type: {"TEMPLATE" if prompt.is_template else "USER PROMPT"}
Favorite: {"★ Yes" if prompt.is_favorite else "No"}
Usage Count: {prompt.usage_count} times
Created: {prompt.created_at.strftime('%Y-%m-%d %H:%M:%S') if prompt.created_at else "N/A"}
Updated: {prompt.updated_at.strftime('%Y-%m-%d %H:%M:%S') if prompt.updated_at else "N/A"}
Last Used: {prompt.last_used_at.strftime('%Y-%m-%d %H:%M:%S') if prompt.last_used_at else "Never"}
Tags: {prompt.tags if prompt.tags else "No tags"}

═══════════════════════════════════════════════════════════════

ROLE:
{prompt.role if prompt.role else "(empty)"}

─────────────────────────────────────────────────────────────

CONTEXT:
{prompt.context if prompt.context else "(empty)"}

─────────────────────────────────────────────────────────────

OBJECTIVE:
{prompt.objective if prompt.objective else "(empty)"}

─────────────────────────────────────────────────────────────

STYLE:
{prompt.style if prompt.style else "(empty)"}

─────────────────────────────────────────────────────────────

TONE:
{prompt.tone if prompt.tone else "(empty)"}

─────────────────────────────────────────────────────────────

AUDIENCE:
{prompt.audience if prompt.audience else "(empty)"}

─────────────────────────────────────────────────────────────

RESPONSE FORMAT:
{prompt.response_format if prompt.response_format else "(empty)"}

─────────────────────────────────────────────────────────────

START ANALYSIS:
{prompt.start_analysis if prompt.start_analysis else "(empty)"}

═══════════════════════════════════════════════════════════════
        """
        
        self.details_display.setText(details)
    
    def load_selected_prompt(self):
        """Load the selected prompt into the main window"""
        current_item = self.prompts_list.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a prompt to load")
            return
        
        prompt_id = current_item.data(Qt.UserRole)
        prompt = self.db.get_prompt(prompt_id)
        
        if not prompt:
            QMessageBox.critical(self, "Error", "Could not load the selected prompt")
            return
        
        # Update main window fields
        self.parent_window.fields["ROLE"].setPlainText(prompt.role or "")
        self.parent_window.fields["CONTEXT"].setPlainText(prompt.context or "")
        self.parent_window.fields["OBJECTIVE"].setPlainText(prompt.objective or "")
        self.parent_window.fields["STYLE"].setPlainText(prompt.style or "")
        self.parent_window.fields["TONE"].setPlainText(prompt.tone or "")
        self.parent_window.fields["AUDIENCE"].setPlainText(prompt.audience or "")
        self.parent_window.fields["RESPONSE FORMAT"].setPlainText(prompt.response_format or "")
        self.parent_window.fields["START ANALYSIS"].setPlainText(prompt.start_analysis or "")
        
        # Increment usage
        self.db.increment_usage(prompt_id)
        
        # Show confirmation
        self.parent_window.statusBar().showMessage(
            f"Loaded prompt: {prompt.title or 'Untitled'}", 3000
        )
        
        # Close the dialog
        self.close()
    
    def delete_selected_prompt(self):
        """Delete the selected prompt with confirmation"""
        current_item = self.prompts_list.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a prompt to delete")
            return
        
        prompt_id = current_item.data(Qt.UserRole)
        prompt = self.db.get_prompt(prompt_id)
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self, 
            "Confirm Delete",
            f"Are you sure you want to delete '{prompt.title or 'Untitled'}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.delete_prompt(prompt_id):
                QMessageBox.information(self, "Success", "Prompt deleted successfully")
                self.load_prompts()  # Refresh list
                self.details_display.clear()
            else:
                QMessageBox.critical(self, "Error", "Could not delete the prompt")
    
    def toggle_favorite(self):
        """Toggle favorite status of selected prompt"""
        current_item = self.prompts_list.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a prompt")
            return
        
        prompt_id = current_item.data(Qt.UserRole)
        is_favorite = self.db.toggle_favorite(prompt_id)
        
        if is_favorite is not None:
            status = "added to favorites" if is_favorite else "removed from favorites"
            QMessageBox.information(self, "Success", f"Prompt {status}")
            self.load_prompts()  # Refresh list
            
            # Re-select and display the updated prompt
            prompt = self.db.get_prompt(prompt_id)
            if prompt:
                self.on_prompt_selected(current_item)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.fields = {}
        self.setWindowTitle("The COSTAR Prompting Helper")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()

    def toggle_dark_mode(self):
        if self.dark_mode_button.isChecked():
            self.setStyleSheet(DARK_MODE_STYLESHEET)
        else:
            self.setStyleSheet("")  # Or revert to default/light stylesheet

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Scroll area for fields
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Clear button
        # clear_button = QPushButton("🗑️ Clear All")
        # clear_button.clicked.connect(self.clear_fields)
        # button_layout.addWidget(clear_button)
        
 

        #  COSTAR fields ORIGINAL
        self.fields = {}
        costar_items = [
            ("ROLE", "Define the role or persona for the AI—financial advisor, expert data scientist, etc. \n(e.g., 'Act as a financial advisor helping clients with retirement plans.')"),
            ("CONTEXT", "Provide background information for the AI to understand your task. \n(e.g., 'I am a 35 year old director associate in a law firm and I am looking for retirement plans.')"),
            ("OBJECTIVE", "Give the specific task(s) for the AI. \n(e.g., 'Your task is to analyze the available retirement plans for my background and assess their pros, cons and cost.')"),
            ("STYLE", "Specify the writing style—professional, casual, technical, simple, etc. \n(e.g., 'Write in a friendly and simple way.')"),
            ("TONE", "Set the emotional tone—formal, friendly, serious, humorous, positive, neutral, etc. \n(e.g., 'Keep the tone professional and encouraging.')"),
            ("AUDIENCE", "Describe the intended audience—students, experts, beginners, customers, executives, etc. \n(e.g., 'The audience is a graduate professional with little financial knowledge.)"),
            ("RESPONSE FORMAT", "Define the format, length, or type of expected response—list, paragraph, summary, table, etc. \n(e.g., 'Provide a bullet-point list with 5 key ideas.')"),
            ("INITIAL ANALYSIS (Optional)", "Ask the AI to confirm its understanding of your request and suggest any missing information. \n(e.g., 'Explain my objectives and suggest anything I missed to accomplish my goals.')")
        ]
        
        for field_name, description in costar_items:
            # Field label with description
            label = QLabel(f"{field_name}")
            label_font = QFont()
            label_font.setBold(True)
            label_font.setPointSize(14)
            label.setFont(label_font)
            
            desc_label = QLabel(description)
            desc_label.setStyleSheet("font-size: 14pt;")


            
            # Text input
            font = QFont()
            font.setPointSize(14)
            text_edit = QTextEdit()
            text_edit.setFont(font)
            text_edit.setMinimumHeight(200)
            text_edit.setMaximumHeight(220)
            
            self.fields[field_name] = text_edit
            
            scroll_layout.addWidget(label)
            scroll_layout.addWidget(desc_label)
            scroll_layout.addWidget(text_edit)
            scroll_layout.addSpacing(14)
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        
        main_layout.addWidget(scroll_area)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Open Saved Prompts button (NEW)
        open_prompts_button = QPushButton("📁 Open Saved Prompts")
        open_prompts_button.clicked.connect(self.open_saved_prompts)
        open_prompts_button.setStyleSheet(
            "background-color: #2196F3; color: white; font-weight: bold; padding: 8px;"
        )
        button_layout.addWidget(open_prompts_button)
        
        # Copy button
        copy_button = QPushButton("📋 Copy Prompt to Clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_button)
        
        # Save button
        save_button = QPushButton("💾 Save Prompt")
        save_button.clicked.connect(self.save_prompt)
        button_layout.addWidget(save_button)
        
        # Clear button
        clear_button = QPushButton("🗑️ Clear All")
        clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(clear_button)
        
        # Dark mode button
        self.dark_mode_button = QPushButton("Dark Mode")
        self.dark_mode_button.setCheckable(True)
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        button_layout.addWidget(self.dark_mode_button)

        main_layout.addLayout(button_layout)
        central_widget.setLayout(main_layout)
    
    def clear_fields(self):
        """Clear all text fields with confirmation"""
        from PySide6.QtWidgets import QMessageBox

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Clear All Fields",
            "Are you sure you want to clear all fields?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            for text_edit in self.fields.values():
                text_edit.clear()
            self.statusBar().showMessage("Fields cleared", 2000)

    def open_saved_prompts(self):
        """Open the dialog to view and manage saved prompts"""
        dialog = PromptHistoryDialog(self)
        dialog.exec()
    
    def copy_to_clipboard(self):
        """Generate prompt text and copy to clipboard"""
        from PySide6.QtGui import QGuiApplication
        
        prompt_data = {}
        for key, text_edit in self.fields.items():
            content = text_edit.toPlainText().strip()
            if content:
                prompt_data[key] = content
        
        if not prompt_data:
            self.statusBar().showMessage("Please fill at least one field", 3000)
            return
        
        # Format prompt with separators for clarity
        prompt_text = "\n\n".join(
            f"# {key} #\n{value}" 
            for key, value in prompt_data.items()
        )
        
        # Copy to clipboard
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(prompt_text)
        
        # Visual feedback
        self.statusBar().showMessage("✓ Prompt copied to clipboard!", 3000)   

    def save_prompt(self):
        """Save prompt to database with optional title and template status"""
        from datetime import datetime
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QMessageBox

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Save Prompt")
        dialog.setModal(True)
        main_layout = QVBoxLayout()

        # Title input
        title_layout = QHBoxLayout()
        title_label = QLabel("Title (optional):")
        title_input = QLineEdit()
        title_layout.addWidget(title_label)
        title_layout.addWidget(title_input)
        main_layout.addLayout(title_layout)

        # Template checkbox
        template_checkbox = QCheckBox("Save as Template")
        template_checkbox.setToolTip("Template prompts can be reused as starters for new prompts")
        main_layout.addWidget(template_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

        # Set up connections
        save_button.clicked.connect(lambda: dialog.accept())
        cancel_button.clicked.connect(lambda: dialog.reject())

        # Set layout
        dialog.setLayout(main_layout)

        # Run dialog
        if dialog.exec():
            # Get values
            title = title_input.text().strip()
            is_template = template_checkbox.isChecked()

            # Get prompt data
            prompt_data = {
                field: text_edit.toPlainText().strip()
                for field, text_edit in self.fields.items()
            }

            # Check if any field has content
            if not any(prompt_data.values()):
                self.statusBar().showMessage("Please fill at least one field", 3000)
                return

            try:
                prompt = PromptTemplate(
                    title=title if title else None,
                    role=prompt_data.get("ROLE", ""),
                    context=prompt_data.get("CONTEXT", ""),
                    objective=prompt_data.get("OBJECTIVE", ""),
                    style=prompt_data.get("STYLE", ""),
                    tone=prompt_data.get("TONE", ""),
                    audience=prompt_data.get("AUDIENCE", ""),
                    response_format=prompt_data.get("RESPONSE FORMAT", ""),
                    start_analysis=prompt_data.get("START ANALYSIS", ""),
                    is_template=is_template,
                    created_at=datetime.now()
                )
                self.db.save_prompt(prompt)
                self.statusBar().showMessage("✓ Prompt saved successfully!", 3000)
            except Exception as e:
                self.statusBar().showMessage(f"Error saving prompt: {str(e)}", 3000)
