# ui/panel_auto.py
import FreeCAD
import FreeCADGui
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
    QtGui = QtWidgets # For compatibility if using Qt6

from .. import facade

class AutoSequencePanel:
    def __init__(self):
        self.form = QtGui.QWidget()
        self.form.setWindowTitle("BendSeq Auto Sequence")
        layout = QtGui.QVBoxLayout(self.form)
        
        import os
        from ..tooling.library import ToolLibrary
        lib_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ToolLibrary")
        self.tool_lib = ToolLibrary(lib_dir)
        
        tool_group = QtGui.QGroupBox("Tool Setup")
        tool_layout = QtGui.QFormLayout()
        
        self.cmb_punch = QtGui.QComboBox()
        punch_names = [p.get("name", p.get("id")) for p in self.tool_lib.data.get("punches", [])]
        if not punch_names: punch_names = ["Default Punch"]
        self.cmb_punch.addItems(punch_names)
        
        self.cmb_die = QtGui.QComboBox()
        die_names = [d.get("name", d.get("id")) for d in self.tool_lib.data.get("dies", [])]
        if not die_names: die_names = ["Default Die"]
        self.cmb_die.addItems(die_names)
        
        tool_layout.addRow("Punch:", self.cmb_punch)
        tool_layout.addRow("Die:", self.cmb_die)
        tool_group.setLayout(tool_layout)
        layout.addWidget(tool_group)
        
        self.btn_run = QtGui.QPushButton("Run Auto Sequence")
        self.btn_run.clicked.connect(self.on_run)
        layout.addWidget(self.btn_run)
        
        self.btn_sim = QtGui.QPushButton("Open Simulation")
        self.btn_sim.setEnabled(False)
        self.btn_sim.clicked.connect(self.on_sim)
        layout.addWidget(self.btn_sim)
        
        self.result_lbl = QtGui.QLabel("Ready. Select the base face of your SheetMetal part.")
        self.result_lbl.setWordWrap(True)
        layout.addWidget(self.result_lbl)
        
        self.last_order = None
        self.last_body = None

    def on_run(self):
        sel = FreeCADGui.Selection.getSelectionEx()
        if not sel:
            self.result_lbl.setText("Error: Please select a base face of the SheetMetal part first.")
            return
            
        self.result_lbl.setText("Running sequence search...")
        QtCore.QCoreApplication.processEvents()
        
        try:
            tool_config = {
                "punch": self.cmb_punch.currentText(),
                "die": self.cmb_die.currentText()
            }
            result = facade.find_sequence(sel, tooling=tool_config)
            if result.get("success"):
                order = result.get("order", [])
                self.last_order = order
                
                # Get the body from selection
                body, _ = facade.freecad_adapter.extract_body_and_base_face(sel)
                self.last_body = body
                
                self.result_lbl.setText(f"Success! Sequence: {', '.join(order)}\nNumbers applied to unfold.")
                self.btn_sim.setEnabled(True)
            else:
                err = result.get("error", "Unknown error")
                self.result_lbl.setText(f"Failed: {err}")
                self.btn_sim.setEnabled(False)
        except Exception as e:
            self.result_lbl.setText(f"Exception during search: {e}")
            
    def on_sim(self):
        if self.last_order and self.last_body:
            from .panel_sim import SimViewerPanel
            # Keep a reference to prevent garbage collection
            self.sim_panel = SimViewerPanel()
            self.sim_panel.load_state(facade.prepare_simulation(self.last_body, self.last_order))
            self.sim_panel.form.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
            self.sim_panel.form.resize(400, 300)
            self.sim_panel.form.show()

class CommandAutoSequence:
    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool1', # Placeholder icon
            'MenuText': 'BendSeq Auto Sequence',
            'ToolTip': 'Automatically find optimal bend sequence'
        }
        
    def Activated(self):
        panel = AutoSequencePanel()
        FreeCADGui.Control.showDialog(panel)

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None
