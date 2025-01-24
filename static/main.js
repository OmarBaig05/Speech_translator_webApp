document.getElementById("translateBtn").addEventListener("click", async () => {
    const text = document.getElementById("originalText").value;
    const language = document.getElementById("languageSelect").value;

    try {
        const response = await fetch("/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, language }),
        });
        const data = await response.json();
        if (data.translated_text) {
            document.getElementById("translatedText").value = data.translated_text;
        } else {
            alert("Error translating text.");
        }
    } catch (error) {
        console.error("Translation error:", error);
    }
});

document.getElementById("speakBtn").addEventListener("click", async () => {
    const text = document.getElementById("translatedText").value;
    const language = document.getElementById("languageSelect").value;

    try {
        const response = await fetch("/speak", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, language }),
        });
        const data = await response.json();
        if (data.audio_url) {
            const audioPlayer = document.getElementById("audioPlayer");
            audioPlayer.src = data.audio_url;
            audioPlayer.play();
        } else {
            alert("Error generating speech.");
        }
    } catch (error) {
        console.error("Speech error:", error);
    }
});
