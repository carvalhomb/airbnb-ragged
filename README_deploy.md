## Deployment instructions

To deploy this app:

1. Build the Docker image
     
     ``` bash
     docker build -t airbnb-ragged .
     ```

2. Run and test the Docker image locally using the `run` command. The `-p`parameter connects our **host port #** to the left of the `:` to our **container port #** on the right.
    
     ``` bash
     docker run -p 7860:7860 airbnb-ragged
     ```

3. Check http://localhost:7860 in the browser to see if the app runs correctly.

4. Create HuggingFace [Huggingface](https://huggingface.co) space.

5. Setup your space as shown below:
   
- Owner: Your username
- Space Name: `airbnb-ragged`
- License: `Openrail`
- Select the Space SDK: `Docker`
- Docker Template: `Blank`
- Space Hardware: `CPU basic - 2 vCPU - 16 GB - Free`
- Repo type: `Public`

6. Clone repo locally, move app files to this repo, and push to HuggingFace.

7. Make sure to add the necessary secrets (OpenAI and Qdrant)

8. Restart space and test!