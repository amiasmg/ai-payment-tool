from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from room_allowance_agent import RoomAllowanceAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app with the correct template directory
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.urandom(24)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the RoomAllowanceAgent
agent = RoomAllowanceAgent(os.getenv("PAYMAN_API_SECRET"))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'room_image' not in request.files:
            return render_template('index.html', error='No image uploaded')
        
        file = request.files['room_image']
        if file.filename == '':
            return render_template('index.html', error='No image selected')
        
        if file:
            # Save the uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Get child's name
                child_name = request.form.get('child_name')
                
                # Process the room and get results
                result = agent.process_room_and_pay(filepath, child_name)
                
                if result:
                    # Add child name to result for display
                    result['child_name'] = child_name
                    return render_template('index.html', result=result)
                else:
                    return render_template('index.html', error='Failed to process room')
                    
            except Exception as e:
                return render_template('index.html', error=str(e))
            finally:
                # Clean up the uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
    
    return render_template('index.html')

@app.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        child_name = request.form.get('child_name')
        amount = float(request.form.get('amount'))
        
        # Get or create payee
        payee = agent.get_or_create_payee(child_name)
        
        # Process payment
        payment = agent.payman.payments.send_payment(
            amount_decimal=amount,
            payee_id=payee["id"],
            memo=f"Allowance for {child_name}"
        )
        
        # Redirect to success page
        return render_template('success.html')
        
    except Exception as e:
        # Redirect to failure page with error message
        return render_template('failure.html', error_message=str(e))

@app.route('/preview/success')
def preview_success():
    return render_template('success.html')

@app.route('/preview/failure')
def preview_failure():
    return render_template('failure.html', error_message="This is a sample error message")

if __name__ == '__main__':
    app.run(debug=True)
