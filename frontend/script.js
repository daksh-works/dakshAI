// Video Upload Handler
const videoForm = document.getElementById("vid-upload");
const videoResultBox = document.getElementById("result");

if (videoForm) 
{
    videoForm.addEventListener("submit", async (e) => 
    {
        e.preventDefault();
        console.log("Video form submitted");

        const file = document.getElementById("videoInput").files[0];

        if (!file) 
        {
            alert("Select a video first");
            return;
        }

        console.log("Video file selected:", file.name);

        const video = document.createElement("video");
        video.preload = "metadata";

        video.onloadedmetadata = async () => 
        {
            window.URL.revokeObjectURL(video.src);
            console.log("Video duration:", video.duration);

            if (video.duration > 20) 
            {
                alert("Video must be less than 20 seconds");
                return;
            }

            videoResultBox.innerText = "Analyzing video...";

            const formData = new FormData();
            formData.append("file", file);

            try 
            {
                console.log("Sending video to backend...");
                const response = await fetch("http://127.0.0.1:8000/analyze", 
                {
                    method: "POST",
                    body: formData
                });

                console.log("Response status:", response.status);
                const data = await response.json();
                console.log("Response data:", data);

                videoResultBox.innerText = data.description;
            } 
            catch (error) 
            {
                console.error("Video analysis error:", error);
                videoResultBox.innerText = "Error analyzing video: " + error.message;
            }
        };

        video.onerror = () => 
        {
            console.error("Error loading video metadata");
            alert("Error loading video file");
        };

        video.src = URL.createObjectURL(file);
    });
}

// Audio Upload Handler
const audioForm = document.getElementById("audio-upload");
const transcribeBox = document.getElementById("transcribe");

if (audioForm) 
{
    
    const audioResultBox = document.querySelectorAll("#result")[1];
    
    audioForm.addEventListener("submit", async (e) => 
    {
        e.preventDefault();
        console.log("Audio form submitted");

        const file = document.getElementById("audioInput").files[0];

        if (!file) 
        {
            alert("Select an audio file first");
            return;
        }

        console.log("Audio file selected:", file.name);

        transcribeBox.innerText = "Processing audio...";
        if (audioResultBox) 
        {
            audioResultBox.innerText = "";
        }

        const formData = new FormData();
        formData.append("file", file);

        try 
        {
            console.log("Sending audio to backend...");
            const response = await fetch("http://127.0.0.1:8000/audio-chat", 
            {
                method: "POST",
                body: formData
            });

            console.log("Response status:", response.status);
            const data = await response.json();
            console.log("Response data:", data);
            
            transcribeBox.innerText = "Transcription: " + data.transcription;
            if (audioResultBox) 
            {
                audioResultBox.innerText = "Response: " + data.response;
            }
        } 
        catch (error) 
        {
            console.error("Audio processing error:", error);
            transcribeBox.innerText = "Error: " + error.message;
            if (audioResultBox) 
            {
                audioResultBox.innerText = "";
            }
        }
    });
}

// Text Chat Handler
const allForms = document.querySelectorAll("form");
let textForm = null;
let textResponseBox = document.getElementById("response");

// Find the first form that doesn't have an ID
for (let i = 0; i < allForms.length; i++) 
{
    if (!allForms[i].id) 
    {
        textForm = allForms[i];
        break;
    }
}

if (textForm && textResponseBox) 
{
    const textarea = textForm.querySelector("textarea");
    const submitButton = textForm.querySelector("button");

    textForm.addEventListener("submit", async (e) => 
    {
        e.preventDefault();
        console.log("Text chat form submitted");

        const userInput = textarea.value.trim();

        if (!userInput) 
        {
            alert("Please type something first");
            return;
        }

        console.log("User input:", userInput);

        submitButton.disabled = true;
        submitButton.innerText = "Processing...";
        textResponseBox.innerText = "Thinking...";

        try 
        {
            console.log("Sending message to backend...");
            const response = await fetch("http://127.0.0.1:8000/chat", 
            {
                method: "POST",
                headers: 
                {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: userInput })
            });

            console.log("Response status:", response.status);
            const data = await response.json();
            console.log("Response data:", data);
            
            textResponseBox.innerText = data.response;
            textarea.value = "";
        } 
        catch (error) 
        {
            console.error("Chat error:", error);
            textResponseBox.innerText = "Error: " + error.message;
        } 
        finally 
        {
            submitButton.disabled = false;
            submitButton.innerText = "Submit";
        }
    });
}

console.log("Script loaded successfully");
console.log("Video form found:", !!videoForm);
console.log("Audio form found:", !!audioForm);
console.log("Text form found:", !!textForm);
