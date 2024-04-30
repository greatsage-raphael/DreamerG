"use client";
import React, { useState, Suspense } from "react";
import Link from "next/link";
import axios from "axios";
import { Canvas } from "@react-three/fiber";
import { useLoader } from "@react-three/fiber";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { OrbitControls } from "@react-three/drei"; // Import OrbitControls

function ModelViewer({ modelUrl }) {
  const gltf = useLoader(GLTFLoader, modelUrl);

  return (
    <Canvas colormanagement="true" style={{ background: "grey" }} key={modelUrl}>
    <ambientLight intensity={2} />
    <directionalLight position={[-20, 5, 2]} intensity={3}  />
    <directionalLight position={[20, 5, 2]} intensity={4} />
    <directionalLight position={[0, 0, -1]} intensity={2} />
    <directionalLight position={[0, 1, 0]} intensity={2} />
    <directionalLight position={[0, -1, 0]} intensity={2} />
  
    <Suspense fallback={null}>
      <primitive object={gltf.scene} scale={1} />
    </Suspense>
    <OrbitControls />
  </Canvas>
  );
}

export default function AIChatbot() {


  const [imageUrl, setImageUrl] = useState("");
  const [modelUrl, setModelUrl] = useState(null);
  const [promptText, setPromptText] = useState("");
  const [outputPrompt, setOutputPrompt] = useState("");
  const [loading, setLoading] = useState(false); // Add a loading state

  const handleTextChange = (event) => {
    setPromptText(event.target.value);
  };

  
  const generate3DModel = async () => {
    setLoading(true);  // Start loading

    const promptData = { message: promptText };
    const formData = new FormData();
    formData.append("prompt", promptText);
    try {
      const response = await axios.post(
        "https://dramerg.onrender.com/text-generate-model-gemini/",
        promptData,
        { responseType: "blob" }
      );

      // Create a URL for the blob
      const modelBlobUrl = URL.createObjectURL(response.data);
      setModelUrl(modelBlobUrl); // Set the URL to the state
      const newPrompt = response.headers['x-new-prompt'];
      console.log(newPrompt)
      setOutputPrompt(newPrompt);  // Update the textarea under viewer_object2
    } catch (error) {
      console.error("Error uploading file", error);
    }
    setLoading(false);  // Stop loading

  };

  const downloadModel = () => {
    const link = document.createElement("a");
    link.href = modelUrl;
    link.download = "3DModel.glb"; // Specify the file name
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <div className="techwave_fn_image_generation_page">
        <div className="generation__page">
          {/* Generation Header */}
          <div className="generation_header">
            <div className="header_top">
              <h1 className="title">Input A Description :</h1>
            </div>

            <div className="header_bottom">
              <div className="include_area">
                <textarea
                  id="fn__include_textarea"
                  value={promptText}
                  onChange={handleTextChange}
                  rows={1}
                />
                
              </div>
           
           
              <div className="generate_section">
              <button
                  id="generate_it"
                  className="techwave_fn_button"
                  onClick={generate3DModel}
                  disabled={loading}  // Disable button when loading
                >
                  {loading ? 'Generating...' : 'Generate'} 
                </button>
                <button className="techwave_fn_button" onClick={downloadModel}>
                  Download
                </button>
                
              </div>
           
            </div>
          </div>

          {/* !Generation Header */}
          <div className="generation_history">
      

          <div className="viewer_object2">

            <h3 className="title2">Gemini Enhance prompt:</h3>
                <textarea
                    id="fn__include_textarea"
                    value={outputPrompt}
                    readOnly  // Make it readOnly if it's only meant to display the output
                    rows={1}
                  />     
          </div>
 
   
            <div className="viewer_object">
              {modelUrl && (
                <div className="viewer3">
                  <ModelViewer modelUrl={modelUrl} />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
