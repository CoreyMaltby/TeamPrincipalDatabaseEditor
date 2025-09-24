import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QFormLayout, QLineEdit, QCheckBox, QDoubleSpinBox, QMessageBox, QStackedWidget, QGroupBox
)
from PyQt6.QtCore import Qt

DATA_DIR = Path("data")
CONFIG_FILE = DATA_DIR / "config.json"


class ConfigTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = self.load_config()

        main_layout = QHBoxLayout(self)
        self.sections = list(self.config.keys())
        self.stack = QStackedWidget()

        # Left buttons
        button_layout = QVBoxLayout()
        for idx, section in enumerate(self.sections):
            btn = QPushButton(section.capitalize())
            btn.clicked.connect(lambda _, i=idx: self.switch_page(i))
            button_layout.addWidget(btn)

            # Build section form
            page = self.build_section_form(section, self.config[section])
            self.stack.addWidget(page)

        button_layout.addStretch()
        main_layout.addLayout(button_layout, 1)
        main_layout.addWidget(self.stack, 3)

        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save_config)
        main_layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignBottom)

    # ---------------- JSON helpers ----------------

    def load_config(self):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    def save_config(self):
        for idx, section in enumerate(self.sections):
            page = self.stack.widget(idx)
            self.config[section] = self.extract_form(page)

        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)

        QMessageBox.information(self, "Saved", "Configuration saved successfully!")

    # ---------------- Form building ----------------

    def build_section_form(self, section_name, data):
        content = QWidget()
        layout = QVBoxLayout(content)

        for key, value in data.items():
            # ---------------- Dirty Air curve ----------------
            if section_name == "dirty_air" and key == "curve" and isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        group = QGroupBox(f"Curve {idx+1}")
                        form = QFormLayout()
                        for subkey, subval in item.items():
                            widget = self.make_widget(subval)
                            form.addRow(QLabel(subkey), widget)
                            widget.setObjectName(f"{key}.{idx}.{subkey}")
                        group.setLayout(form)
                        layout.addWidget(group)
                    else:
                        # fallback
                        widget = self.make_widget(item)
                        layout.addWidget(QLabel(f"Curve {idx}"))
                        layout.addWidget(widget)

            # ---------------- Tyres ----------------
            elif section_name == "tyres":
                # Compounds
                if key == "compounds":
                    for comp_name, comp_data in value.items():
                        group = QGroupBox(comp_name.capitalize())
                        form = QFormLayout()
                        for subkey, subval in comp_data.items():
                            widget = self.make_widget(subval)
                            form.addRow(QLabel(subkey), widget)
                            widget.setObjectName(f"{key}.{comp_name}.{subkey}")
                        group.setLayout(form)
                        layout.addWidget(group)

                # Temperature effects
                elif key == "temperature_effects":
                    for temp_key, temp_data in value.items():
                        group = QGroupBox(f"Temperature {temp_key.capitalize()}")
                        form = QFormLayout()
                        for main_key, main_val in temp_data.items():
                            if main_key == "compounds":
                                for comp_name, comp_vals in main_val.items():
                                    for subkey, subval in comp_vals.items():
                                        widget = self.make_widget(subval)
                                        form.addRow(QLabel(f"{comp_name}.{subkey}"), widget)
                                        widget.setObjectName(f"{key}.{temp_key}.compounds.{comp_name}.{subkey}")
                            else:
                                widget = self.make_widget(main_val)
                                form.addRow(QLabel(main_key), widget)
                                widget.setObjectName(f"{key}.{temp_key}.{main_key}")
                        group.setLayout(form)
                        layout.addWidget(group)

                # Wetness effects
                elif key == "wetness_effects":
                    for wet_key, wet_data in value.items():
                        group = QGroupBox(f"Wetness {wet_key.replace('_',' ').capitalize()}")
                        form = QFormLayout()
                        for main_key, main_val in wet_data.items():
                            if main_key == "compounds":
                                for comp_name, comp_vals in main_val.items():
                                    for subkey, subval in comp_vals.items():
                                        widget = self.make_widget(subval)
                                        form.addRow(QLabel(f"{comp_name}.{subkey}"), widget)
                                        widget.setObjectName(f"{key}.{wet_key}.compounds.{comp_name}.{subkey}")
                            else:
                                widget = self.make_widget(main_val)
                                form.addRow(QLabel(main_key), widget)
                                widget.setObjectName(f"{key}.{wet_key}.{main_key}")
                        group.setLayout(form)
                        layout.addWidget(group)

                # Start probabilities
                elif key == "start_probabilities":
                    group = QGroupBox("Start Probabilities")
                    form = QFormLayout()
                    for comp_name, prob in value.items():
                        widget = self.make_widget(prob)
                        form.addRow(QLabel(comp_name), widget)
                        widget.setObjectName(f"{key}.{comp_name}")
                    group.setLayout(form)
                    layout.addWidget(group)

                # Other Tyre fields
                else:
                    widget = self.make_widget(value)
                    form_group = QFormLayout()
                    form_group.addRow(QLabel(key), widget)
                    container = QWidget()
                    container.setLayout(form_group)
                    layout.addWidget(container)
                    widget.setObjectName(key)

            # ---------------- Other sections ----------------
            else:
                widget = self.make_widget(value)
                form_group = QFormLayout()
                form_group.addRow(QLabel(key), widget)
                container = QWidget()
                container.setLayout(form_group)
                layout.addWidget(container)
                widget.setObjectName(key)

        # Scrollable wrapper
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        return scroll

    def make_widget(self, value):
        if isinstance(value, bool):
            w = QCheckBox()
            w.setChecked(value)
            return w
        elif isinstance(value, (int, float)):
            w = QDoubleSpinBox()
            w.setRange(-1e6, 1e6)
            w.setDecimals(4)
            w.setValue(float(value))
            return w
        elif isinstance(value, str):
            return QLineEdit(value)
        elif isinstance(value, list):
            return QLineEdit(",".join(map(str, value)))
        else:
            return QLineEdit(str(value))

    # ---------------- Extract form values ----------------

    def extract_form(self, scroll_widget):
        result = {}
        content = scroll_widget.widget()
        layout = content.layout()

        def process_layout(layout, parent_keys=[]):
            for i in range(layout.count()):
                item = layout.itemAt(i)
                w = item.widget()
                if isinstance(w, QGroupBox):
                    process_layout(w.layout(), parent_keys + [w.title()])
                elif isinstance(w, QWidget):
                    inner_layout = w.layout()
                    if inner_layout:
                        process_layout(inner_layout, parent_keys)
                    else:
                        if hasattr(w, "objectName") and w.objectName():
                            key_path = w.objectName().split(".")
                            self.set_nested_value(result, key_path, self.read_widget(w))

        process_layout(layout)
        return result

    def set_nested_value(self, d, keys, value):
        for k in keys[:-1]:
            if k.isdigit():
                k = int(k)
                while len(d) <= k:
                    d.append({})
                d = d[k]
            else:
                d = d.setdefault(k, {})
        last_key = keys[-1]
        if last_key.isdigit():
            last_key = int(last_key)
            while len(d) <= last_key:
                d.append(None)
            d[last_key] = value
        else:
            d[last_key] = value

    def read_widget(self, widget):
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QDoubleSpinBox):
            return widget.value()
        elif isinstance(widget, QLineEdit):
            text = widget.text()
            if "," in text:
                try:
                    return [float(x) if "." in x else int(x) for x in text.split(",")]
                except ValueError:
                    return text.split(",")
            return text
        else:
            return None

    # ---------------- Navigation ----------------

    def switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
