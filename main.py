from youtube_transcript_api import YouTubeTranscriptApi
from summarizer1 import text_summarizer
import re
import nltk

# Download required NLTK data at startup
def download_nltk_resources():
    print("Checking and downloading required NLTK resources...")
    resources = ['punkt', 'stopwords']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
            print(f"Resource '{resource}' is already downloaded.")
        except LookupError:
            print(f"Downloading resource '{resource}'...")
            nltk.download(resource)
    print("NLTK resources check completed.")

def clean_transcript_text(text):
    """Clean transcript text by removing timestamps, special characters, and transcription artifacts."""
    # Remove text within square brackets (like [Music])
    text = re.sub(r'\[.*?\]', '', text)
    # Remove transcription artifacts
    artifacts = ['Laughter', 'Applause', 'Music', 'Cheering', 'Audience', 'Clapping']
    for artifact in artifacts:
        text = re.sub(rf'\b{artifact}\b', '', text, flags=re.IGNORECASE)
    # Remove multiple spaces and clean up
    text = ' '.join(text.split())
    # Remove any standalone punctuation
    text = re.sub(r'\s+[^\w\s]+\s+', ' ', text)
    return text.strip()

def extract_video_id(url):
    """Extract video ID from YouTube URL, handling various URL formats."""
    # Extract the base video ID
    if "youtube.com/watch?v=" in url:
        # Handle URLs with parameters
        video_id = url.split("youtube.com/watch?v=")[1]
        # Remove any additional parameters (like &t=109s)
        if "&" in video_id:
            video_id = video_id.split("&")[0]
        return video_id
    elif "youtu.be/" in url:
        # Handle shortened URLs
        video_id = url.split("youtu.be/")[1]
        if "?" in video_id:
            video_id = video_id.split("?")[0]
        return video_id
    else:
        raise ValueError("Invalid YouTube URL. Please provide a valid YouTube video URL.")

def YT_summarizer(url):
    print("URL: ",url)

    # Extract video ID from URL
    try:
        video_id = extract_video_id(url)
        print("Video id: ",video_id)
    except ValueError as e:
        raise e

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
    # Remove any double periods that might have been added
    extracted_text = re.sub(r'\.+', '.', extracted_text)
    
    # Check if we have enough meaningful text
    if meaningful_entries < 5:
        raise ValueError("This video doesn't have enough meaningful text to summarize. It might be a music video or contain mostly non-text content.")

    print(f"\nExtracted {meaningful_entries} meaningful segments of text.")
    
    # Get desired summary length
    while True:
        try:
            num_words = int(input("Enter the desired number of words you want for the summary (5-1000): "))
            if 5 <= num_words <= 1000:
                break
            print("Please enter a number between 5 and 1000.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Generate summary
    try:
        summarized_text = text_summarizer(extracted_text, num_words)
        return summarized_text
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Download required NLTK resources at startup
    download_nltk_resources()
    
    # Python Tutorial - Python Full Course for Beginners
    video_url = "https://www.youtube.com/watch?v=_uQrJ0TkZlc"
    
    try:
        summary = YT_summarizer(video_url)
        print("\nSummary of the video:")
        print(summary)
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nPlease try a different video that has more spoken content.")