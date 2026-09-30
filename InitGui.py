import FreeCAD
import FreeCADGui

class BendSeqWorkbench(FreeCADGui.Workbench):
    MenuText = "BendSeq"
    ToolTip = "BendSeq - SheetMetal Sequence Generation"
    Icon = """
        /* XPM */
        static const char * const dummy_icon[] = {
        "16 16 2 1",
        "  c None",
        ". c #000000",
        "                ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "  ............  ",
        "                "
        };
        """

    def Initialize(self):
        from BendSeq.ui.panel_auto import CommandAutoSequence
        from BendSeq.ui.panel_sim import CommandSimViewer
        
        FreeCADGui.addCommand('BendSeq_AutoSequence', CommandAutoSequence())
        FreeCADGui.addCommand('BendSeq_SimViewer', CommandSimViewer())
        
        self.appendToolbar("BendSeq", ["BendSeq_AutoSequence", "BendSeq_SimViewer"])
        self.appendMenu("BendSeq", ["BendSeq_AutoSequence", "BendSeq_SimViewer"])
        FreeCAD.Console.PrintLog("BendSeq Workbench initialized.\n")

    def GetClassName(self):
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(BendSeqWorkbench())
