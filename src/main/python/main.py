from fbs_runtime.application_context.PyQt5 import ApplicationContext
import sys

from PyQt5 import QtQml, QtCore, QtGui
import PyQt5.QtQuick

from rdapp import App
from rdcanvas import RDCanvas
from context import *
from timeline import TimelineModel
from logger import Logger

dirname = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QML2_IMPORT_PATH'] = os.path.join(dirname, 'qml')
import sys

import os
os.makedirs(QtCore.QStandardPaths.locate(QtCore.QStandardPaths.DocumentsLocation, "", QtCore.QStandardPaths.LocateDirectory) + "rdapp/projects", exist_ok=True)
os.makedirs(QtCore.QStandardPaths.locate(QtCore.QStandardPaths.DocumentsLocation, "", QtCore.QStandardPaths.LocateDirectory) + "rdapp/render", exist_ok=True)
os.makedirs(QtCore.QStandardPaths.locate(QtCore.QStandardPaths.DocumentsLocation, "", QtCore.QStandardPaths.LocateDirectory) + "rdapp/snap", exist_ok=True)

# Application Subclassing

from PyQt5.QtWidgets import QApplication
from fbs_runtime.application_context import cached_property
from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, pyqtProperty as Property

class MyQApplication(QApplication):
	load_project = Signal(str)
	def event(self, event):
		if event.type() == QtCore.QEvent.FileOpen:
			url = event.url().toString().replace('file://', '')
			self.load_project.emit(url)
		return QApplication.event(self, event)



class MyApplicationContext(ApplicationContext):
	@cached_property
	def app(self):
		return MyQApplication(sys.argv)

if __name__ == "__main__":

	surfaceFormat = QtGui.QSurfaceFormat()
	surfaceFormat.setMajorVersion(3)
	surfaceFormat.setMinorVersion(3)
	surfaceFormat.setProfile(QtGui.QSurfaceFormat.CoreProfile)
	QtGui.QSurfaceFormat.setDefaultFormat(surfaceFormat)

	logger = Logger()
	appctx = MyApplicationContext()
	os.environ["PATH"] += os.pathsep + os.path.split(appctx.get_resource("ffprobe"))[0]
	os.environ["IMAGEIO_FFMPEG_EXE"] = appctx.get_resource("ffmpeg")

	import shutil

	prj_folder = QtCore.QStandardPaths.locate(QtCore.QStandardPaths.DocumentsLocation, "", QtCore.QStandardPaths.LocateDirectory) + "rdapp/projects"
	prj_default = appctx.get_resource("projects")
	for prj in [f for f in os.listdir(appctx.get_resource("projects")) if os.path.isfile(os.path.join(prj_default, f))]:
		p_def = os.path.join(prj_default, prj)
		p_new = os.path.join(prj_folder, prj)
		if not os.path.exists(p_new):
			shutil.copyfile(p_def, p_new)

	QtGui.QFontDatabase.addApplicationFont(appctx.get_resource("fonts/JetBrainsMono-Regular.ttf"))
	QtGui.QFontDatabase.addApplicationFont(appctx.get_resource("fonts/JetBrainsMono-Medium-Italic.ttf"))
	QtGui.QFontDatabase.addApplicationFont(appctx.get_resource("fonts/JetBrainsMono-Medium.ttf"))
	QtGui.QFontDatabase.addApplicationFont(appctx.get_resource("fonts/JetBrainsMono-Italic.ttf"))
	QtGui.QFontDatabase.addApplicationFont(appctx.get_resource("fonts/JetBrainsMono-ExtraBold-Italic.ttf"))
	QtGui.QFontDatabase.addApplicationFont(appctx.get_resource("fonts/JetBrainsMono-ExtraBold.ttf"))
	QtGui.QFontDatabase.addApplicationFont(appctx.get_resource("fonts/JetBrainsMono-Bold-Italic.ttf"))
	QtGui.QFontDatabase.addApplicationFont(appctx.get_resource("fonts/JetBrainsMono-Bold.ttf"))
	font = QtGui.QFont("jetbrains mono")
	font.setPixelSize(17)
	appctx.app.setFont(font)
	appctx.app.setOrganizationName("Radugadesign")
	appctx.app.setOrganizationDomain("radugadesign.com")
	appctx.app.setApplicationName("rdapp")
	screen = appctx.app.primaryScreen()

	prj = None
	if len(sys.argv) > 1:
		if os.path.exists(sys.argv[1]):
			prj = sys.argv[1]
	app = App(appctx.get_resource(""), prj)


	model = Model(app)
	style = StyleContext(app)
	configGeneral = ConfigModelGeneral(app)
	configRender = ConfigModelRender(app)
	configPreview = ConfigModelPreview(app, style)
	configProject = ConfigModelProject(app)
	timeline = TimelineModel()
	con = Controller(appctx, app, timeline, model, [configGeneral, configRender, configPreview, configProject], style, logger)
	codeEditorContext = CodeEditorContext(style)

	engine = QtQml.QQmlApplicationEngine()
	context = engine.rootContext()
	context.setContextProperty("codeEditorContext", codeEditorContext)
	context.setContextProperty("logger", logger)
	context.setContextProperty("con", con)
	context.setContextProperty("md", model)
	context.setContextProperty("configGeneral", configGeneral)
	context.setContextProperty("configRender", configRender)
	context.setContextProperty("configPreview", configPreview)
	context.setContextProperty("configProject", configProject)
	context.setContextProperty("timeline", timeline)
	context.setContextProperty("style", style)
	engine.load(appctx.get_resource("main.qml"))
	if not engine.rootObjects():
		sys.exit(-1)

	exit_code = appctx.app.exec_()
	sys.exit(exit_code)