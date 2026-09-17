## Problem statements and Target User
People who use sign language may face communication difficulties when interacting with people who do not understand sign language. In situations such as schools, workplaces, hospitals, shops, and public services, the lack of a common communication method can make conversations slower and more difficult.

Our application uses Artificial Intelligence and computer vision to identify sign language motions via a camera and instantly translate them into textual subtitles. This allows people who do not understand sign language to read the translated message on the application. 

## User Inputs
The main input will be video captured through the device's camera.
Users will perform sign-language gestures in front of the camera. The system will process information such as:
- Hand position and movement
- Hand shape
- Finger positions
- Sequence of gestures (to ensure whatever was signed is understandable to the person on the receiving end)

For example:
**Camera Input → Sign Language Gestures → AI Processing → Text Subtitle**

### Considerations
A key project consideration is that sign languages are different from one another. Therefore, the project would be focused solely on **Singapore Sign Language (SgSL)**, rather than attempting to recognise every sign language.

Another consideration would be that the hand signs shown are in an environment with ample lighting (such that the hand sign shown is clear and visible)

## Use of AI
AI will be used primarily for computer vision and gesture recognition. The camera captures the user's movements, and an AI model analyses the video frames to identify the signs being performed.

The system could use a machine-learning/deep-learning model trained using sign-language video or image datasets.
The general process will be:

**Capture**: The camera records the user's signing.

**Detection**: The system identifies the user's hand movements.

**Feature Extraction**: Important characteristics such as hand position, shape, and movement are extracted.

**AI Recognition**: The trained AI model predicts the sign or sequence of signs.

**Language Processing**: Recognised signs are converted into understandable words.

**Subtitle Generation**: The translated words are displayed on the screen.

**Data Persistence**: The translated words are logged onto a database in relation to each sign detected.

**Data Loading**: Previous data are used together with current detection to boost detection confidence.


## Business Rules

### Sign Validity
A recognised sign is only accepted as valid if, the AI confidence score and the same predicted sign 	appears consistently across the frames. If it fails, the application flags the segment and displays eg. “Please repeat the sign” instead of a subtitle.

### Supported signs/vocabulary checks
If the predicted sign label fails outside the trained dataset’s label set, the application rejects it rather than guessing the closest match, and prompts the user to repeat or use a supported sign.

### Sentence processing/assembly
Accepted signs are added to the end of the output sentence in the order they were made. The system does not change the order or guess grammar rules beyond basic punctuation and capitalisation, keeping the user's original meaning.