# BlockBallot
BlockBallot is a decentralized electronic voting platform that combines blockchain integrity with biometric authentication to ensure secure, transparent, and tamper-proof elections. Designed for multi-category voting scenarios, this system leverages facial recognition, QR-based document validation, and cryptographic vote verification to protect voter identity and election outcomes.

🚀 Why This Project Matters
Traditional electronic voting systems often struggle with trust, security, and accessibility. This project reimagines digital voting by:
- Ensuring vote immutability through blockchain
- Preventing fraud with biometric and document-based authentication
- Empowering institutions to run transparent, auditable elections

🔐 Key Features
🧱 Blockchain Implementation
- Immutable vote records stored in decentralized blocks
- SHA-256 hashing and Proof-of-Work consensus
- Merkle tree for vote verification
- Transaction-based voting with traceable vote IDs
🧠 Multi-Layer Authentication
- Facial recognition via webcam
- QR code document validation
- Secure password-based login
🗂️ Election Management
- Support for multiple candidate categories
- Real-time vote tracking and automated result tabulation
- Anti-fraud mechanisms and double-vote prevention



⚙️ Installation Guide
### Clone the repository
```
git clone https://github.com/graduallywatermelon/BlockBallot/
cd BlockBallot
```
### Create and activate virtual environment
```
python -m venv venv
```
##### Windows
```
.\venv\Scripts\activate
```
##### Linux/MacOS
```
source venv/bin/activate
```
### Install dependencies
```
pip install -r requirements.txt
```

💡 Use run.bat to launch the project. It spins up two blockchain nodes. More nodes can be added via a cURL request to the /register_with endpoint of any node.


🧭 Usage Guide
👨‍💼 For Administrators
- Access admin panel: http://localhost:5000/admin
- Default credentials: admin / pass
- Admin Functions:
- Register voters
- Add/remove candidates
- Monitor election progress
- Declare results
- Manage blockchain nodes
🧑‍💻 For Voters
- Vote at http://localhost:5000/vote:
- Allow camera permission to complete face verification
- Upload voter ID for QR scan
- Enter Password
- Select Candidates
- Confirm Vote
- Receive blockchain transaction ID

✅ Vote Verification
- Use transaction ID to verify vote
- Check vote status on blockchain
- View published results

🧱 Blockchain Structure
Block {
    timestamp: datetime
    votes: List[Vote]
    previous_hash: str
    nonce: int
    hash: str
}



🔒 Security Highlights
Blockchain Security
- Immutable vote records
- Cryptographic verification
- Distributed consensus
- Tamper-evident blocks
Authentication Security
- Biometric verification
- QR document validation
- Encrypted passwords
- Session management
System Security
- Double-vote prevention
- Data encryption
- Secure communication
- Audit trails

🧪 Troubleshooting
If you encounter issues:
- Make Sure to register as a voter before trying to vote
- Ensure upload id has a valid qr which stores a id matching the format uid="([A-Z]+\d+)"
- Ensure webcam and QR scanner permissions are granted

🤝 Contributing
- Fork the repository
- Create a feature branch
- Commit your changes
- Push to your branch
- Submit a pull request

📄 License
This project is licensed under the MIT License. See the LICENSE file for details.

📬 Support
For technical queries or feature requests, please open an issue.
