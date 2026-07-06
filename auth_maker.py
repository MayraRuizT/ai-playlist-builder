import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

def create_credentials_token():
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
    
    if not os.path.exists('client_secret.json'):
        print("❌ Error: Move your client_secret.json file into this folder first!")
        return

    # Use standard out-of-band loop to completely avoid network port bindings
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', 
        SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print("\n🔗 STEP 1: Copy and paste this URL into your browser bar:")
    print(auth_url)
    
    print("\n🔐 STEP 2: Log in, hit allow, and copy the long string Google shows you.")
    auth_code = input("\n📥 STEP 3: Paste that string here and press Enter: ").strip()
    
    try:
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # Save token file directly into your app directory
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            
        print("\n🎉 SUCCESS! 'token.pickle' file has been securely created.")
        print("You can now launch your Streamlit web app smoothly!")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")

if __name__ == "__main__":
    create_credentials_token()

