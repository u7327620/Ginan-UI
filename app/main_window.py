from app.controllers.file_dialog import FileDialogController
from app.views.main_window_ui import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow
from app.controllers.config_controller import ConfigController 
import yaml

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.processButton.clicked.connect(self.on_process_clicked)
        self.models = []
        self.controllers = []
        self.setup_controllers()


    def setup_controllers(self):
        self.controllers.append(FileDialogController(self.ui, "")) # no model for now
        self.controllers.append(ConfigController(self.ui))

    def on_process_clicked(self):
        # 从界面中提取用户输入
        mode = self.ui.Mode.currentText()
        constellation = self.ui.Constellations_2.currentText()
        receiver = self.ui.Receiver_type.currentText()
        antenna = self.ui.Antenna_type.currentText()
        ppp_provider = self.ui.PPP_provider.currentText()
        ppp_series = self.ui.PPP_series.currentText()
        antenna_offset = self.ui.antennaOffsetValue.text()

        print("提取用户输入：")
        print("  模式:", mode)
        print("  星座系统:", constellation)
        print("  接收机类型:", receiver)
        print("  天线类型:", antenna)
        print("  PPP 提供商:", ppp_provider)
        print("  PPP 系列:", ppp_series)
        print("  天线偏移:", antenna_offset)
        print("✅ 按钮被点击了！")

    # 生成配置字典
        config = {
        'mode': mode,
        'constellation': constellation,
        'receiver_type': receiver,
        'antenna_type': antenna,
        'ppp_provider': ppp_provider,
        'ppp_series': ppp_series,
        'antenna_offset': antenna_offset
    }

    # 写入 YAML 文件
        self.write_yaml(config)

    def write_yaml(self, config: dict):
        with open("config.yaml", "w", encoding="utf-8") as f:
          yaml.dump(config, f, allow_unicode=True)
        print("配置文件 config.yaml 写入成功！")



      
    
   
