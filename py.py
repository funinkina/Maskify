from langdetect import detect


def detect_language(text):
    try:
        language = detect(text)
        return language
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Example usage
if __name__ == "__main__":
    sample_text = "ji bol raha hu"
    detected_language = detect_language(sample_text)
    if detected_language:
        print(f"The detected language is: {detected_language}")
    else:
        print("Could not detect the language.")
