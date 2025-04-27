
        text = re.sub(rf'\b{artifact}\b', '', text, flags=re.IGNORECASE)
    # Remove multiple spaces and clean up
    text = ' '.join(text.split())
    # Remove any standalone punctuation
    text = re.sub(r'\s+[^\w\s]+\s+', ' ', text)
    return text.strip()

def YT_summarizer(url):
    print("URL: ",url)

    # Extract video ID from URL
    if "youtube.com/watch?v=" not in url:
        raise ValueError("Invalid YouTube URL. Please provide a URL in the format: https://www.youtube.com/watch?v=VIDEO_ID")
    
    video_id = url.replace("https://www.youtube.com/watch?v=","")
    print("Video id: ",video_id)

    # Get transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print("Found transcript with", len(transcript), "entries")
    except Exception as e:
        raise Exception(f"Could not get transcript. Error: {str(e)}")

    # Extract and clean text
    extracted_text = ""
    meaningful_entries = 0
    for entry in transcript:
        text = clean_transcript_text(entry['text'])
        if text and len(text) > 3:  # Skip very short entries
            extracted_text += f'. {text}'  # Add period to help with sentence separation
            meaningful_entries += 1
    
    # Clean up the final text
    extracted_text = extracted_text.strip()