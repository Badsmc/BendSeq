# ui/panel_sim.py
import FreeCAD
import FreeCADGui
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
    QtGui = QtWidgets

from .. import facade

class SimViewerPanel:
    def __init__(self):
        self.form = QtGui.QWidget()
        self.form.setWindowTitle("BendSeq Simulation Viewer")
        layout = QtGui.QVBoxLayout(self.form)
        
        self.lbl = QtGui.QLabel("Simulation Viewer: Load a sequence first.")
        layout.addWidget(self.lbl)
        
        btn_layout = QtGui.QHBoxLayout()
        self.btn_prev = QtGui.QPushButton("< Step Backward")
        self.btn_play = QtGui.QPushButton("Play/Pause")
        self.btn_next = QtGui.QPushButton("Step Forward >")
        
        self.btn_prev.clicked.connect(self.on_prev)
        self.btn_play.clicked.connect(self.on_play)
        self.btn_next.clicked.connect(self.on_next)
        
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_play)
        btn_layout.addWidget(self.btn_next)
        
        layout.addLayout(btn_layout)
        
        self.viewer = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_timer)

    def load_state(self, state):
        from ..simulation.viewer import Viewer
        self.viewer = Viewer(state)
        self.update_ui()
        
    def update_ui(self):
        if not self.viewer:
            return
        step = self.viewer.state.current_step
        total = self.viewer.state.total_steps
        self.lbl.setText(f"Simulation Step {step} / {total}")
        
    def on_prev(self):
        if self.viewer:
            self.viewer.step_backward()
            self.update_ui()
            
    def on_next(self):
        if self.viewer:
            self.viewer.step_forward()
            self.update_ui()
            
    def on_play(self):
        if not self.viewer:
            return
        if self.viewer.is_playing:
            self.viewer.pause()
            self.timer.stop()
        else:
            self.viewer.play()
            self.timer.start(50) # Assuming 50ms per tick
            
    def on_timer(self):
        if self.viewer and self.viewer.is_playing:
            # Stub: in a real implementation this would trigger smooth animation steps
            # For now, just step whole bends every ~1 sec (20 ticks)
            if not hasattr(self, '_tick_count'):
                self._tick_count = 0
            self._tick_count += 1
            if self._tick_count >= 20:
                self._tick_count = 0
                if self.viewer.state.current_step < self.viewer.state.total_steps:
                    self.viewer.step_forward()
                    self.update_ui()
                else:
                    self.viewer.pause()
                    self.timer.stop()

class CommandSimViewer:
    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool2',
            'MenuText': 'BendSeq Simulation Viewer',
            'ToolTip': 'View bend sequence simulation'
        }
        
    def Activated(self):
        panel = SimViewerPanel()
        
        # Try to pull latest sequence if available in a real app
        # panel.load_state(facade.prepare_simulation(body, order))
        
        FreeCADGui.Control.showDialog(panel)

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None
