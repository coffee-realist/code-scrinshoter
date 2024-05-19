import sys
import os

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow, QVBoxLayout,
                             QPushButton, QTreeWidget, QTreeWidgetItem, QWidget,
                             QMessageBox, QCheckBox, QLabel, QScrollArea, QInputDialog)

from code_parser import Code
from code_to_png import CodeToPng


class CodeExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Explorer")
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.open_button = QPushButton("Open Python Code File", self)
        self.open_button.clicked.connect(self.open_file)
        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(["Code Structure"])
        self.concat_check = QCheckBox("Concatenate Screenshots", self)
        self.select_button = QPushButton("Get Code Screenshots", self)
        self.select_button.clicked.connect(self.select_item)
        self.copy_button = QPushButton("Copy Image", self)
        self.copy_button.clicked.connect(self.copy_image_to_clipboard)
        self.copy_button.setEnabled(False)
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_image_as)
        self.save_button.setEnabled(False)
        self.image_layout_widget = QWidget()
        self.image_layout = QVBoxLayout(self.image_layout_widget)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_layout_widget)
        self.layout.addWidget(self.open_button)
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.concat_check)
        self.layout.addWidget(self.select_button)
        self.layout.addWidget(self.copy_button)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.scroll_area)
        self.code_structure = None
        self.current_image_paths = []

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Code File", "", "Python Files (*.py)")
        if file_path:
            self.code_structure = Code(file_path)
            self.populate_tree()

    def populate_tree(self):
        self.tree.clear()
        if self.code_structure:
            if self.code_structure.libraries_code:
                lib_item = QTreeWidgetItem([f"Libraries (Lines {self.code_structure.libraries_code.start_line}-"
                                            f"{self.code_structure.libraries_code.end_line})"])
                lib_item.obj = self.code_structure.libraries_code
                self.tree.addTopLevelItem(lib_item)
            for cls in self.code_structure.classes:
                cls_item = self.add_class_item(cls)
                self.tree.addTopLevelItem(cls_item)
            for func in self.code_structure.functions:
                func_item = self.add_function_item(func)
                self.tree.addTopLevelItem(func_item)
            if self.code_structure.global_code:
                global_item = QTreeWidgetItem([f"Global Code (Lines {self.code_structure.global_code.start_line}-"
                                               f"{self.code_structure.global_code.end_line})"])
                global_item.obj = self.code_structure.global_code
                self.tree.addTopLevelItem(global_item)

    def add_class_item(self, cls):
        item = QTreeWidgetItem([f"Class: {cls.name} (Lines {cls.start_line}-{cls.end_line})"])
        item.obj = cls
        for method in cls.functions:
            method_item = self.add_function_item(method)
            item.addChild(method_item)
        for inner_class in cls.classes:
            inner_class_item = self.add_class_item(inner_class)
            item.addChild(inner_class_item)
        return item

    def add_function_item(self, func):
        item = QTreeWidgetItem([f"Function: {func.name} (Lines {func.start_line}-{func.end_line})"])
        item.obj = func
        for inner_func in func.functions:
            inner_func_item = self.add_function_item(inner_func)
            item.addChild(inner_func_item)
        for inner_class in func.classes:
            inner_class_item = self.add_class_item(inner_class)
            item.addChild(inner_class_item)
        return item

    def select_item(self):
        def clear_image_layout():
            for i in reversed(range(self.image_layout.count())):
                widget_to_remove = self.image_layout.itemAt(i).widget()
                self.image_layout.removeWidget(widget_to_remove)
                widget_to_remove.setParent(None)

        selected_item = self.tree.currentItem()
        if selected_item:
            code_obj = selected_item.obj
            code_text = self.code_structure.get_code(code_obj)
            concat_screenshots = self.concat_check.isChecked()
            ctp = CodeToPng(code_text)
            ctp.save_code_pages('code', concat_screenshots=concat_screenshots)
            clear_image_layout()
            self.current_image_paths = []
            if concat_screenshots:
                self.current_image_paths = ['code_concat.png']
            else:
                part = 1
                while os.path.exists(f'code_part{part}.png'):
                    self.current_image_paths.append(f'code_part{part}.png')
                    part += 1
            for image_path in self.current_image_paths:
                pixmap = QPixmap(image_path)
                image_label = QLabel(self)
                image_label.setPixmap(pixmap)
                self.image_layout.addWidget(image_label)
            self.copy_button.setEnabled(True)
            self.save_button.setEnabled(True)

    def copy_image_to_clipboard(self):
        if not self.current_image_paths:
            return

        if len(self.current_image_paths) == 1:
            clipboard = QApplication.clipboard()
            pixmap = QPixmap(self.current_image_paths[0])
            clipboard.setPixmap(pixmap)
        else:
            items = [os.path.basename(path) for path in self.current_image_paths]
            item, ok = QInputDialog.getItem(self, "Select Image", "Choose image to copy:", items, 0, False)
            if ok and item:
                selected_image_path = self.current_image_paths[items.index(item)]
                pixmap = QPixmap(selected_image_path)
                clipboard = QApplication.clipboard()
                clipboard.setPixmap(pixmap)

    def save_image_as(self):
        if not self.current_image_paths:
            return

        save_directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if save_directory:
            for image_path in self.current_image_paths:
                base_name = os.path.basename(image_path)
                save_path = os.path.join(save_directory, base_name)
                pixmap = QPixmap(image_path)
                pixmap.save(save_path)
            QMessageBox.information(self, "Save Complete", "All images have been saved successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    explorer = CodeExplorer()
    explorer.show()
    sys.exit(app.exec_())
