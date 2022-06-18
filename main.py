from flask import Flask, render_template
from PIL import Image
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
import os
import secrets
import extcolors
from colormap import rgb2hex


class UploadForm(FlaskForm):
    image = FileField('Upload Image', validators=[DataRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Upload')


app = Flask(__name__)
app.config['SECRET_KEY'] = '1c8a76ef845ebc5456d7fd1dfebbb1af59529922'
bootstrap = Bootstrap(app)


def save_img(file):
    hex_name = secrets.token_hex(5)
    _, file_ext = os.path.splitext(file.filename)
    new_name = hex_name+file_ext
    file_path = os.path.join(app.root_path, "static/images_uploaded", new_name)
    i = Image.open(file)
    i.save(file_path)
    return new_name, file_path


def extract_hex(input):
    colors_pre_list = str(input).replace('([(', '').split(', (')[0:-1]
    df_rgb = [i.split('), ')[0] + ')' for i in colors_pre_list]
    df_percent = [i.split('), ')[1].replace(')', '') for i in colors_pre_list]

    # convert RGB to HEX code
    df_color_up = [rgb2hex(int(i.split(", ")[0].replace("(", "")),
                           int(i.split(", ")[1]),
                           int(i.split(", ")[2].replace(")", ""))) for i in df_rgb]

    # df = pd.DataFrame(zip(df_color_up, df_percent), columns = ['c_code','occurence'])
    return df_color_up


@app.route('/', methods=['POST', 'GET'])
def home():
    form = UploadForm()
    hex_colors = None
    img_name = None
    # Get the path where uploaded files will be stored.
    pat = os.path.join(app.root_path, "static/images_uploaded")
    if form.validate_on_submit():
        # Delete Existing File to keep the folder clean
        for filename in os.listdir(pat):
            if filename != 'work.jpg':
                to_delete = os.path.join(pat, filename)
                os.remove(to_delete)
        # Save the uploaded image
        img_name, img_path = save_img(form.image.data)
        # Extract the RGB colors from the image
        colors_x = extcolors.extract_from_path(img_path, tolerance=12, limit=10)
        # Convert rgb to Hex
        hex_colors = extract_hex(colors_x)
    return render_template('index.html', form=form, hex_colors=hex_colors, image=img_name)


if __name__ == "__main__":
    app.run(debug=True)
