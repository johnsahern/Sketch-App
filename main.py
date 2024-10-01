from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.utils import platform
import os
import subprocess

# Vérification si l'application tourne sur Android
if platform == 'android':
    from android.permissions import request_permissions, Permission

class SketchApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_image_path = None
        self.transformed_image_path = None

    def build(self):
        # Couleur de fond sombre par défaut
        Window.clearcolor = (0.15, 0.15, 0.15, 1)

        # Layout principal
        self.layout = FloatLayout()

        # Titre de l'application
        title = Label(
            text="🖼️ Image Sketch 🖌️",
            size_hint=(1, 0.1),
            pos_hint={"y": 0.9},
            color=(1, 1, 1, 1),
            font_size='24sp'
        )
        self.layout.add_widget(title)

        # Image affichée
        self.image = Image(size_hint=(1, 0.55), pos_hint={"y": 0.35})
        self.layout.add_widget(self.image)

        # Bouton d'upload
        self.btn_upload = Button(
            text="📁 Upload Image",
            size_hint=(0.3, 0.1),
            pos_hint={"x": 0.35, "y": 0.205},
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='18sp',
            on_release=self.check_android_permissions
        )
        self.layout.add_widget(self.btn_upload)

        # Bouton pour appliquer la transformation
        self.btn_apply = Button(
            text="🖌️ Apply Transformation",
            size_hint=(0.3, 0.1),
            pos_hint={"x": 0.35, "y": 0.1049},
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='18sp',
            on_release=self.apply_transformation
        )
        self.layout.add_widget(self.btn_apply)

        # Bouton pour sauvegarder l'image transformée
        self.btn_save = Button(
            text="💾 Save Image",
            size_hint=(0.3, 0.1),
            pos_hint={"x": 0.35, "y": 0.001},
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='18sp',
            on_release=self.save_image
        )
        self.layout.add_widget(self.btn_save)

        # ProgressBar
        self.progress_bar = ProgressBar(max=100, size_hint=(1, None), height=20, pos_hint={"y": 0.3})
        self.layout.add_widget(self.progress_bar)

        return self.layout

    def check_android_permissions(self, instance):
        if platform == 'android':
            # Demander les permissions si nécessaire
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE], self.open_file_manager)
        else:
            self.open_file_manager(instance)

    def open_file_manager(self, *args):
        content = FileChooserListView()
        content.bind(on_submit=self.load_image)
        self.popup = Popup(title="Select an Image", content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def load_image(self, filechooser, selection, *args):
        if selection:
            self.selected_image_path = selection[0]
            self.image.source = self.selected_image_path
            self.image.reload()
            self.popup.dismiss()

    def apply_transformation(self, *args):
        output_step1 = os.path.join(os.path.dirname(self.selected_image_path), "output_step1.png")
        output_step2 = os.path.join(os.path.dirname(self.selected_image_path), "output_step2.png")
        output_step3 = os.path.join(os.path.dirname(self.selected_image_path), "output_step3.png")

        try:
            subprocess.run(['python', 'step1.py', self.selected_image_path, output_step1], check=True)
            subprocess.run(['python', 'step2.py', output_step1, output_step2], check=True)
            subprocess.run(['python', 'step3.py', output_step2, output_step3], check=True)

            self.transformed_image_path = output_step3
            self.image.source = self.transformed_image_path
            self.image.reload()

            if os.path.exists(output_step1):
                os.remove(output_step1)
            if os.path.exists(output_step2):
                os.remove(output_step2)

            self.progress_bar.value = 100

        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de la transformation: {e}")

    def save_image(self, *args):
        content = FloatLayout()
        self.file_name_input = TextInput(hint_text='Enter file name', size_hint=(0.5, 0.2), pos_hint={"y": 0.5, "x": 0.25})
        content.add_widget(self.file_name_input)

        btn_save = Button(text='Save file', size_hint=(0.5, 0.2), pos_hint={"y": 0.3, "x": 0.25})
        btn_save.bind(on_release=self.save_file)
        content.add_widget(btn_save)

        self.popup = Popup(title="Save Transformed Image", content=content, size_hint=(0.5, 0.3))
        self.popup.open()

    def save_file(self, instance):
        file_name = self.file_name_input.text.strip()
        if file_name:
            save_path = os.path.join(os.path.dirname(self.selected_image_path), f"{file_name}.png")
            try:
                os.rename(self.transformed_image_path, save_path)
                print(f"Image saved as {save_path}")
                self.popup.dismiss()
            except Exception as e:
                print(f"Erreur lors de la sauvegarde de l'image: {e}")
        else:
            print("Aucun nom de fichier entré.")

if __name__ == "__main__":
    SketchApp().run()
