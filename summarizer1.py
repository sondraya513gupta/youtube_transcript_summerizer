import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from string import punctuation
import re

def clean_text(text):
    """Clean the text by removing special characters and normalizing whitespace."""
    # Remove special characters and keep only letters, numbers, and basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', ' ', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    # Ensure proper spacing around punctuation
    text = re.sub(r'\s*([.,!?])\s*', r'\1 ', text)
    return text.strip()

def text_summarizer(text, num_words):
    """
    Summarize the given text to approximately the specified number of words using extractive summarization.
    
    Args:
        text (str): The text to be summarized
        num_words (int): Target number of words for the summary
        
    Returns:
        str: The summarized text
    """
    if not text or not text.strip():
        raise ValueError("Empty text provided")

    # Clean the text
    text = clean_text(text)
    
    # Use the NLTK resources downloaded at startup
    # (These should already be downloaded in main.py)
    
    # Tokenize the text into sentences
    try:
        sentences = sent_tokenize(text)
    except Exception as e:
        raise Exception(f"Error tokenizing sentences: {str(e)}")
        
    if not sentences:
        raise ValueError("No sentences found in the text")

    # Tokenize into words and clean
    try:
        words = word_tokenize(text.lower())
    except Exception as e:
        raise Exception(f"Error tokenizing words: {str(e)}")
        
    if not words:
        raise ValueError("No words found in the text")
    
    # Remove stopwords and punctuation, but keep important words
    try:
        stop_words = set(stopwords.words('english')) - {'how', 'what', 'why', 'when', 'where', 'who'}
        stop_words.update(punctuation)
        words = [word for word in words if word not in stop_words and word.isalnum()]
    except Exception as e:
        # If there's any error with stopwords, use a simpler approach
        words = [word for word in words if word.isalnum() and len(word) > 2]
    
    if not words:
        raise ValueError("No meaningful words found after cleaning")
    
    # Calculate word frequencies
    word_freq = FreqDist(words)
    
    # Score sentences based on word frequencies and position
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        score = 0
        try:
            sent_words = word_tokenize(sentence.lower())
        except:
            # Fallback if tokenization fails
            sent_words = sentence.lower().split()
        
        # Score based on word frequency
        for word in sent_words:
            if word in word_freq:
                score += word_freq[word]
        
        # Normalize by sentence length
        score = score / (len(sent_words) + 1)  # +1 to avoid division by zero
        
        # Give higher weight to sentences at the beginning and end
        position_weight = 1.0
        if i < len(sentences) * 0.3:  # First 30% of sentences
            position_weight = 1.3
        elif i > len(sentences) * 0.7:  # Last 30% of sentences
            position_weight = 1.2
        
        sentence_scores[sentence] = score * position_weight
    
    # Sort sentences by score
    sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Select top sentences until we reach approximately the desired word count
    summary = []
    word_count = 0
    
    # If we have very few sentences, use all of them
    if len(sorted_sentences) <= 3:
        summary = [sent for sent, _ in sorted_sentences]
    else:
        # Keep track of sentence indices to maintain original order
        selected_sentences = []
        max_word_count = min(num_words * 1.2, 2000)  # Cap at 2000 words to avoid excessive processing
        
        for sentence, _ in sorted_sentences:
            # Count words in the simplest way if tokenization fails
            try:
                sentence_word_count = len(word_tokenize(sentence))
            except:
                sentence_word_count = len(sentence.split())
                
            if word_count + sentence_word_count > max_word_count:
                break
            
            try:
                selected_sentences.append((sentences.index(sentence), sentence))
                word_count += sentence_word_count
            except:
                # If the sentence somehow isn't in the original list, skip it
                continue
        
        # Sort by original position to maintain flow
        summary = [sent for _, sent in sorted(selected_sentences)]
    
    if not summary:
        # If we couldn't generate a summary, return a portion of the original text
        words_in_text = text.split()
        if len(words_in_text) > num_words:
            return ' '.join(words_in_text[:num_words]) + '...'
        return text
    
    # Join sentences and return
    return ' '.join(summary) 