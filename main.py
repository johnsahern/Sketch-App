from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.lang import Builder
import os
import subprocess
from plyer import filechooser
from kivy.utils import platform
from plyer import filechooser
from kivy.utils import platform
from jnius import autoclass

Builder.load_string('''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<ModernButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    canvas.before:
        Color:
            rgba: get_color_from_hex('#2196F3') if self.state == 'normal' else get_color_from_hex('#1976D2')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]
    font_name: 'Roboto'
    bold: True
    color: 1, 1, 1, 1

<ModernProgressBar@ProgressBar>:
    canvas:
        Color:
            rgba: get_color_from_hex('#E3F2FD')
        RoundedRectangle:
            pos: self.x, self.center_y - dp(4)
            size: self.width, dp(8)
            radius: [dp(4)]
        Color:
            rgba: get_color_from_hex('#2196F3')
        RoundedRectangle:
            pos: self.x, self.center_y - dp(4)
            size: self.width * (self.value / 100.0), dp(8)
            radius: [dp(4)]

<CustomPopup@Popup>:
    background: ''
    background_color: 0, 0, 0, 0.8
    separator_height: 0
    title_size: dp(18)
    title_color: 1, 1, 1, 1
    
<ModernTextInput@TextInput>:
    background_color: 0.95, 0.95, 0.95, 1
    foreground_color: 0.1, 0.1, 0.1, 1
    cursor_color: get_color_from_hex('#2196F3')
    padding: [dp(10), dp(10), dp(10), dp(10)]
    font_size: dp(16)
    multiline: False
''')

class SketchApp(App):
    selected_image_path = StringProperty(None)
    transformed_image_path = StringProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Image Sketch Studio'  # Set the window title
        self.theme_cls = {
            'primary': '#2196F3',
            'primary_dark': '#1976D2',
            'background': '#121212',
            'surface': '#1E1E1E',
            'error': '#CF6679'
        }

    def build(self):
        Window.clearcolor = get_color_from_hex('#121212')
        
        self.layout = FloatLayout()
        
        self.container = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(20)],
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Changed from self.title to header_label
        self.header_label = Label(
            text="Image Sketch Studio",
            font_size=dp(28),
            color=(1, 1, 1, 0.87),
            size_hint_y=None,
            height=dp(50),
            bold=True
        )
        self.container.add_widget(self.header_label)
        
        self.image_container = BoxLayout(
            size_hint_y=0.6,
            padding=[dp(10)],
        )
        self.image = Image(
            source='',
            allow_stretch=True,
            keep_ratio=True
        )
        self.image_container.add_widget(self.image)
        self.container.add_widget(self.image_container)
        
        self.progress_bar = ProgressBar(
            max=100,
            size_hint_y=None,
            height=dp(20),
            value=0
        )
        self.container.add_widget(self.progress_bar)
        
        buttons_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(180)
        )
        
        # Upload button
        self.btn_upload = Button(
            text="Select Image",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex('#2196F3'),
            color=(1, 1, 1, 1),
            on_release=self.check_android_permissions
        )
        buttons_layout.add_widget(self.btn_upload)
        
        # Transform button
        self.btn_transform = Button(
            text="Transform Image",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex('#2196F3'),
            color=(1, 1, 1, 1),
            on_release=self.apply_transformation
        )
        buttons_layout.add_widget(self.btn_transform)
        
        # Save button
        self.btn_save = Button(
            text="Save Result",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex('#2196F3'),
            color=(1, 1, 1, 1),
            on_release=self.save_image
        )
        buttons_layout.add_widget(self.btn_save)
        
        self.container.add_widget(buttons_layout)
        self.layout.add_widget(self.container)
        
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            from android.storage import primary_external_storage_path
            self.storage_path = primary_external_storage_path()
            
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
        
        return self.layout

    def check_android_permissions(self, instance):
        if platform == 'android':
            from android.storage import primary_external_storage_path
            from android import mActivity
            from android.permissions import request_permissions, Permission, check_permission

            def on_permissions_callback(permissions, grant_results):
                if all(grant_results):
                    Clock.schedule_once(lambda dt: self.open_file_manager())

            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ], on_permissions_callback)
        else:
            self.open_file_manager()

    def open_file_manager(self, *args):
        if platform == 'android':
            # Use jnius to trigger Android's file chooser
            filechooser = autoclass('android.content.Intent')
            intent = filechooser(filechooser.ACTION_GET_CONTENT)
            intent.setType("image/*")
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            PythonActivity.mActivity.startActivityForResult(intent, 1)
        else:
            # For non-Android platforms, open standard file chooser
            content = FileChooserListView()
            content.bind(on_submit=self.load_image)
            self.popup = Popup(title="Select an Image", content=content, size_hint=(0.9, 0.9))
            self.popup.open()

    def load_image(self, filechooser, selection, *args):
        if selection:
            self.selected_image_path = selection[0]
            self.image.source = self.selected_image_path
            self.image.reload()
            if hasattr(self, 'popup'):
                self.popup.dismiss()        


    def apply_transformation(self, *args):
        if not self.selected_image_path:
            self.show_error_popup("Please select an image first")
            return

        self.progress_bar.value = 0
        
        try:
            app_dir = self.get_application_directory()
            output_step1 = os.path.join(app_dir, "output_step1.png")
            output_step2 = os.path.join(app_dir, "output_step2.png")
            output_step3 = os.path.join(app_dir, "output_step3.png")

            def update_progress(value):
                Animation(value=value, duration=0.3).start(self.progress_bar)

            Clock.schedule_once(lambda dt: update_progress(33), 0.1)
            subprocess.run(['python', 'step1.py', self.selected_image_path, output_step1], check=True)
            
            Clock.schedule_once(lambda dt: update_progress(66), 0.2)
            subprocess.run(['python', 'step2.py', output_step1, output_step2], check=True)
            
            Clock.schedule_once(lambda dt: update_progress(100), 0.3)
            subprocess.run(['python', 'step3.py', output_step2, output_step3], check=True)

            self.transformed_image_path = output_step3
            self.image.source = self.transformed_image_path
            self.image.reload()

            for file in [output_step1, output_step2]:
                if os.path.exists(file):
                    os.remove(file)

        except Exception as e:
            self.show_error_popup(f"Transformation error: {str(e)}")
            self.progress_bar.value = 0

    def save_image(self, *args):
        if not self.transformed_image_path:
            self.show_error_popup("No transformed image to save")
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        self.file_name_input = TextInput(
            hint_text='Enter file name',
            size_hint_y=None,
            height=dp(50),
            multiline=False
        )
        content.add_widget(self.file_name_input)
        
        btn_save = Button(
            text='Save',
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex('#2196F3'),
            color=(1, 1, 1, 1),
            on_release=self.save_file
        )
        content.add_widget(btn_save)

        self.popup = Popup(
            title="Save Image",
            content=content,
            size_hint=(0.8, None),
            height=dp(200)
        )
        self.popup.open()

    def save_file(self, instance):
        file_name = self.file_name_input.text.strip()
        if not file_name:
            self.show_error_popup("Please enter a file name")
            return

        try:
            # Déterminer le répertoire de sauvegarde
            save_dir = self.get_application_directory()
            save_path = os.path.join(save_dir, f"{file_name}.png")

            # renommer le fichier transformé
            if hasattr(self, 'transformed_image_path') and os.path.exists(self.transformed_image_path):
                os.rename(self.transformed_image_path, save_path)  # Renomme le fichier
                self.show_success_popup(f"Image saved to {file_name}.png")
                self.popup.dismiss()
            else:
                self.show_error_popup("No transformed image found to rename.")
        except Exception as e:
            self.show_error_popup(f"Error renaming file: {str(e)}")

    def get_application_directory(self):
        if platform == 'android':
            from android.storage import primary_external_storage_path
            app_dir = os.path.join(primary_external_storage_path(), 'ImageSketch')
        else:
            app_dir = os.path.join(os.path.dirname(__file__), 'output')
            
        os.makedirs(app_dir, exist_ok=True)
        return app_dir

    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, color=(1, 0.8, 0.8, 1)))
        
        popup = Popup(
            title='Error',
            content=content,
            size_hint=(0.8, None),
            height=dp(150)
        )
        popup.open()

    def show_success_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, color=(0.8, 1, 0.8, 1)))
        
        popup = Popup(
            title='Success',
            content=content,
            size_hint=(0.8, None),
            height=dp(150)
        )
        popup.open()

if __name__ == "__main__":
    SketchApp().run()
