import streamlit as st
import streamlit_authenticator as sa
from google.cloud import storage
from google.oauth2 import service_account
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Image, Part

st.set_page_config(
        page_title="Image Analyzer Prototype",
)

# Constants
PROJECT_ID = st.secrets['project_id']
BUCKET_NAME = st.secrets['bucket_name']
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcs_connections"]) 

vertexai.init(project=PROJECT_ID, location="us-central1", credentials=credentials)
multimodal_model = GenerativeModel("gemini-1.0-pro-vision")



# Initialize Google Cloud Storage client
client = storage.Client(project=PROJECT_ID, credentials=credentials)

# Function to upload file to GCS
def upload_to_gcs(file_path):
    blob_name = os.path.basename(file_path)
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    return f"gs://{BUCKET_NAME}/{blob_name}"

generic_prompt= """

Your role is to explain images in an online course for students with vision difficulties. 
Frame your answers using natural language and easy-to-understand words.
Describe all important details of the image that would be important for a student to understand. 

You have two tasks:

First: Provide a one-sentence alternative text description of the image.

Second: Provide a long description of the image describing the following features in detail. 
Think through each step by step:
1. What is the image showing?
2. What are the key features of this image that a student should understand?
4. What is the primary takeaway and purpose of including this image in the course?

Follow this format in returning your response:

-Alt Text: {response}
-Long Description: {response} 

"""
complex_prompt= """

Your role is to explain images in an online course for students with vision difficulties. 
Frame your answers using natural language and easy-to-understand words.
Describe all important details of the image that would be important for a student to understand. 

You have two tasks:

First: Provide a one-sentence alternative text description of the image.

Second: Provide a long description of the image describing the following features in detail. 
Think through each step by step:
1. What is the image showing?
2. What are the key features of this image that a student should understand?
4. What is the primary takeaway and purpose of including this image in the course?

Follow this format in returning your response:

-Alt Text: {response}
-Long Description: {response} 

"""

visualization_prompt= """

Your role is to analyze data visualizations in an online course for students with vision difficulties. 
Frame your answers using natural language and easy-to-understand words.
Describe all important details of the visualization that would be important for a student to understand. 

You have two tasks:

First: Provide a one-sentence alternative text description of the visualization.

Second: Provide a long description of the data visualization describing the following features in detail. 
Think through each step by step:
1. Understand the type of visualization used (stacked area chart, line graph, bar chart, etc.)
2. Determine the key metrics and axis dimensions included in the visualization
3. Determine the overall trend or message communicated in the visualization
4. Provide any key takeaway message

Follow this format in returning your response:

-Alt Text: {response}
-Long Description: {response} 

"""

other_prompt= """

Your role is to analyze images in an online course for students with vision difficulties. 
Frame your answers using natural language and easy-to-understand words.
Describe all important details of the visualization that would be important for a student to understand. 

You have two tasks:

First: Provide a one-sentence alternative text description of the visualization.

Second: Provide a long description of the data visualization describing its features in detail. 
Think through each step by step:
1. What is this image showing?
2. What are any details you can extract? (e.g., words, locations, people)
2. What is the purpose of including this image in the course?
4. Provide any key takeaway message or emotion the image is inteded to convey to sighted learners. 

Follow this format in returning your response:

-Alt Text: {response}
[new line]
-Long Description: {response} 

"""

# Streamlit app
def main():
    st.title("Image Analyzer Prototype :sparkles:")
    st.write("Upload images to create alt text and long descriptions.")

    image_type = st.radio(
    "What type of images are you analyzing?",
    ["Generic Images :frame_with_picture:", "Complex Diagrams :repeat:", "Data Visualizations :chart_with_upwards_trend:", "Other :woman-shrugging:"],
    captions = ["Stock Images, Photography, Simple Graphics",
                 "Scientific Illustrations, Process Workflows, Detailed Graphics",
                   "Statistical Charts, Complex Data Visualizations",
                   "Anything else..."])

    image_files = st.file_uploader("Choose your images...", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

    if image_files:

        with st.spinner('Wait for it...'):
            
            for image in image_files:

                
                #st.write(image.name)
                

                # Save the uploaded image to a temporary file
                with open(f"{image.name}", "wb") as temp_file:
                    temp_file.write(image.getvalue())

                # Analyze image with Gemini and generate a response
                
                # Print image and Gemini Response
                
                # Upload the image to Google Cloud Storage
                gcs_url = upload_to_gcs(f"{image.name}")

                st.write(image.name + " upload successful!")
                st.write(f"Image URL: {gcs_url}")

                # Query the model based on image type selection

                if image_type == 'Generic Images':

                    response = multimodal_model.generate_content(
                        [
                            # Add an example image
                            Part.from_uri(
                                f"{gcs_url}", mime_type="image/jpeg"
                            ),
                            # Add an example query
                            f"{generic_prompt}",
                        ],
                        generation_config={
                            "max_output_tokens": 2048,
                            "temperature":.4            }
                    )
                    st.image(image, caption=f"{response.text}", use_column_width=True)
                    #st.write(response.text)
                elif image_type == 'Complex Diagrams':
                    response = multimodal_model.generate_content(
                        [
                            # Add an example image
                            Part.from_uri(
                                f"{gcs_url}", mime_type="image/jpeg"
                            ),
                            # Add an example query
                            f"{complex_prompt}",
                        ],
                        generation_config={
                            "max_output_tokens": 2048,
                            "temperature":.4            }
                    )
                    st.image(image, caption=f"{response.text}", use_column_width=True)
                    #st.write(response.text)
                
                elif image_type == 'Data Visualizations':
                    response = multimodal_model.generate_content(
                        [
                            # Add an example image
                            Part.from_uri(
                                f"{gcs_url}", mime_type="image/jpeg"
                            ),
                            # Add an example query
                            f"{visualization_prompt}",
                        ],
                        generation_config={
                            "max_output_tokens": 2048,
                            "temperature":.4            }
                    )
                    st.image(image, caption=f"{response.text}", use_column_width=True)
                    #st.write(response.text)
                
                else:
                   response = multimodal_model.generate_content(
                        [
                            # Add an example image
                            Part.from_uri(
                                f"{gcs_url}", mime_type="image/jpeg"
                            ),
                            # Add an example query
                            f"{other_prompt}",
                        ],
                        generation_config={
                            "max_output_tokens": 2048,
                            "temperature":.4            }
                    )
                   st.image(image, caption=f"{response.text}", use_column_width=True)
                    #st.write(response.text) 
        
        st.success('All images completed!')

        
if __name__ == "__main__":
    
    password = st.text_input("Password", type="password")
    
    if password == st.secrets["password"]:
        main()
    else:
        st.error("Access denied.")
