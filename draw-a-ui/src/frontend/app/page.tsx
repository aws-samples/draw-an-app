"use client";

import dynamic from "next/dynamic";
import "@tldraw/tldraw/tldraw.css";
import { useEditor } from "@tldraw/tldraw";
import { getSvgAsImage } from "@/lib/getSvgAsImage";
import { blobToBase64 } from "@/lib/blobToBase64";
import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";
import { PreviewModal } from "@/components/PreviewModal"; 

const Tldraw = dynamic(async () => (await import("@tldraw/tldraw")).Tldraw, {
  ssr: false,
});

export default function Home() {
  const [html, setHtml] = useState<null | string>(null);

  useEffect(() => {
    const listener = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setHtml(null);
      }
    };
    window.addEventListener("keydown", listener);

    return () => {
      window.removeEventListener("keydown", listener);
    };
  });

  return (
    <>
      <div className={`w-screen h-screen`}>
        <Tldraw persistenceKey="tldraw">
          <ExportButton setHtml={setHtml} />
        </Tldraw>
      </div>
      {html &&
        ReactDOM.createPortal(
          <div
            className="fixed top-0 left-0 right-0 bottom-0 flex justify-center items-center"
            style={{ zIndex: 2000, backgroundColor: "rgba(0,0,0,0.5)" }}
            onClick={() => setHtml(null)}
          >
            <PreviewModal html={html} setHtml={setHtml} />
          </div>,
          document.body
        )}
    </>
  );
}

function ExportButton({ setHtml }: { setHtml: (html: string) => void }) {
  const editor = useEditor();
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<'claude' | 'llama'>('claude');

  // A tailwind styled button that is pinned to the bottom right of the screen
  return (
    <div className="fixed bottom-4 right-4 flex items-center gap-2" style={{ zIndex: 1000 }}>
      <select
        value={selectedModel}
        onChange={(e) => setSelectedModel(e.target.value as 'claude' | 'llama')}
        className="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5"
      >
        <option value="claude">Claude</option>
        <option value="llama">Llama</option>
      </select>
      <button
        onClick={async (e) => {
          setLoading(true);
          try {
            e.preventDefault();
            const svg = await editor.getSvg(
              Array.from(editor.currentPageShapeIds)
            );
            if (!svg) {
              return;
            }
            const png = await getSvgAsImage(svg, {
              type: "png",
              quality: 1,
              scale: 1,
            });
            const dataUrl = await blobToBase64(png!);
            
            const endpoint = selectedModel === 'claude' 
              ? "/api/toHtml"
              : "/api/toHtmlLlama";

            //await fetch("/api/toHtml"  
            const resp = await fetch(`${endpoint}`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ image: dataUrl }),
            });

            const json = await resp.json();
            console.log(json)

            if (json.error) {
              alert("Error from API: " + JSON.stringify(json.error));
              return;
            }

            const message = json.html;
            const start = message.indexOf("<!DOCTYPE html>");
            const end = message.indexOf("</html>");
            const html = message.slice(start, end + "</html>".length);
            setHtml(html);
          } finally {
            setLoading(false);
          }
        }}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        disabled={loading}
      >
        {loading ? (
          <div className="flex justify-center items-center ">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          </div>
        ) : (
          "Generate"
        )}
      </button>
    </div>
  );
}
