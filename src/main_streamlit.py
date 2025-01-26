import streamlit as st
import traceback
from utils.project_utils import initialize, reset_project, update_project
from utils.image_utils import process_image
from utils.aws_utils import invoke_model

def main():
    st.set_page_config(page_title="Draw-an-App", layout="wide")
    st.title("Draw-an-App")
    st.write("Upload an image of your app design to generate the code.")

    # Initialize on first run
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.bedrock_runtime, st.session_state.system_prompt, st.session_state.chat_prompt = initialize()

    # File uploader
    uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])

    if uploaded_file is not None:
        # Display original image
        from PIL import Image
        image = Image.open(uploaded_file)
        image = image.resize((1120, 1120))
        st.image(image, caption="Original Image", use_column_width=True)

        if st.button("Generate App"):
            with st.spinner("Processing..."):
                # Reset project
                st.text("Resetting project...")
                reset_project()

                # Process image
                st.text("Processing image...")
                processed_image = process_image(image)
                st.image(processed_image, caption="Processed Image", use_column_width=True)

                # Call LLM
                st.text("Generating app code...")
                try:
                    response = invoke_model(
                        st.session_state.bedrock_runtime,
                        st.session_state.system_prompt,
                        st.session_state.chat_prompt,
                        processed_image
                    )
                    
                    # Update project
                    st.text("Updating project...")
                    update_project(response)
                    
                    st.success("App generated successfully! 🎉")
                    st.balloons()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.text(traceback.format_exc())

if __name__ == "__main__":
    main()
