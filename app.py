import plotly.express as px
from plotly.graph_objects import Figure
import cv2
from dash import Dash, dcc, html, Input, Output, no_update, callback
import dash_uploader as du
import json
import os
import uuid
from src.autocrop import autocrop

#img = cv2.imread("test/data/img_2024-05-17_120000 copy.jpg")

#print(img.shape)
fig = Figure()

session_id = str(uuid.uuid4())
# fig = px.imshow(img, aspect="auto")
# fig.layout.autosize = False

# fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgb(0,0,0,0)")
# fig.update_layout(dragmode="drawrect", newshape=dict(line_color='red'))
# fig.update_layout(modebar_add=
#     [
#         "drawrect",
#         "eraseshape",
#     ]
# )

# crop_data = pd.read_csv("./test/data/crop.txt", sep="\t", header=None)

# keys = []
# values = []
# for plant in range(len(crop_data)):
#         # Get ID (path to each 'cropped' folder)
#         plant_ID = crop_data.iloc[plant,0] #
#         plant_ID = plant_ID.split(" ")[0] # Split by " "; take the first
#         keys.append(plant_ID) # Add this to the 'keys' list
#         # print(f"Processing {plant_ID}...")
#         # Get coordinates
#         coords = crop_data.iloc[plant,0]
#         coords = coords.split(" ")[1:]  # This must change if using \t sep!!
#         coords = [int(i) for i in coords] # Convert values to integers
#         values.append(tuple(coords))  # Append coords as tuple

# regions = dict(zip(keys, values))

# for plant, coords in regions.items():
#     fig.add_shape(
#         type="rect",
#         x0=coords[0],
#         y0=coords[1],
#         x1=coords[0]+ coords[2],
#         y1=coords[1] + coords[3],
#         line_color='red',
#         editable=True
#     )

app = Dash(__name__)
du.configure_upload(app, r"./userdata")

app.layout = html.Div(
    [
        html.H3("circadia"),
        du.Upload(
                  id='dash-uploader',
                  text='Drag and Drop Here to upload!',
                  text_completed='Uploaded: ',
                  text_disabled='The uploader is disabled.',
                  cancel_button=True,
                  pause_button=False,
                  disabled=False,
                  filetypes=None,
                  max_file_size=1024,
                  chunk_size=1,
                  default_style=None,
                  upload_id=session_id,
                  max_files=1000000,
                  )
,
        dcc.Graph(id="graph-picture", figure=fig),
        dcc.Markdown("Characteristics of shapes"),
        html.Pre(id="annotations-data"),
    ]
)

# @callback(
#     Output("graph-picture", "figure"),
#     Input("dash-uploader", "fileNames"),
#     prevent_initial_call=True
# )
# def update_image(fileNames):
#     if fileNames is not None:
#         print(fileNames)
#         decoded = cv2.imdecode()
#         fig = px.imshow(decoded, aspect="auto")
#         fig.layout.autosize = False
#         fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgb(0,0,0,0)")
#         fig.update_layout(dragmode="drawrect", newshape=dict(line_color='red'))
#         fig.update_layout(modebar_add=
#             [
#                 "drawrect",
#                 "eraseshape",
#             ]
#         )
#         return fig
#     else:
#         return no_update


@du.callback(
    output=Output('graph-picture', 'figure'),
    id='dash-uploader',
)
def update_image(filenames):
    rectangles = autocrop("./userdata/" + session_id, 12, 0, 10)
    start_image = cv2.imread(os.path.join(".", filenames[0]))
    fig = px.imshow(start_image, aspect="auto")
    fig.layout.autosize = False

    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgb(0,0,0,0)")
    fig.update_layout(dragmode="drawrect", newshape=dict(line_color='red'))
    fig.update_layout(modebar_add=
        [
            "drawrect",
            "eraseshape",
        ]
    )
    for rectangle in rectangles:
        fig.add_shape(
            type="rect",
            x0=rectangle[0],
            y0=rectangle[1],
            x1=rectangle[0]+ rectangle[2],
            y1=rectangle[1] + rectangle[3],
            line_color='red',
            editable=True
        )
    return fig

     
@callback(
    Output("annotations-data", "children"),
    Input("graph-picture", "relayoutData"),
    prevent_initial_call=True,
)
def on_new_annotation(relayout_data):
    if "shapes" in relayout_data:
        return json.dumps(relayout_data["shapes"], indent=2)
    else:
        return no_update


if __name__ == "__main__":
    app.run(debug=True)
