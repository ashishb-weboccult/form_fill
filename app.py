import streamlit as st
import uuid
from dataclasses import dataclass
from typing import Dict, Optional
import re

# Configure page
st.set_page_config(
    page_title="Hospital Patient Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for hospital theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57, #20B2AA);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .section-header {
        background: #F0F8FF;
        color: #2E8B57;
        padding: 0.8rem;
        border-radius: 8px;
        border-left: 4px solid #2E8B57;
        margin: 1rem 0;
    }
    
    .patient-card {
        background: #F8FFFF;
        border: 1px solid #B0E0E6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .success-message {
        background: #E8F5E8;
        border: 1px solid #90EE90;
        border-radius: 5px;
        padding: 1rem;
        color: #006400;
    }
    
    .error-message {
        background: #FFE8E8;
        border: 1px solid #FFB6C1;
        border-radius: 5px;
        padding: 1rem;
        color: #DC143C;
    }
    
    .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #2E8B57 !important;
        font-weight: 500;
    }
    
    .sidebar .sidebar-content {
        background: #F0F8FF;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class Patient:
    """Patient data model"""
    hospital_id: str
    name: str
    age: int
    gender: str
    phone: str
    address: str
    
    def to_dict(self) -> Dict:
        """Convert patient object to dictionary"""
        return {
            'hospital_id': self.hospital_id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address
        }

class PatientDatabase:
    """In-memory patient database - easily replaceable with SQLite/PostgreSQL"""
    
    def __init__(self):
        if 'patients_db' not in st.session_state:
            st.session_state.patients_db = {}
    
    def save_patient(self, patient: Patient) -> bool:
        """Save patient to database"""
        try:
            st.session_state.patients_db[patient.phone] = patient.to_dict()
            return True
        except Exception as e:
            st.error(f"Database error: {str(e)}")
            return False
    
    def get_patient_by_phone(self, phone: str) -> Optional[Dict]:
        """Retrieve patient by phone number"""
        return st.session_state.patients_db.get(phone)
    
    def get_patient_by_id(self, hospital_id: str) -> Optional[Dict]:
        """Retrieve patient by hospital ID"""
        for patient_data in st.session_state.patients_db.values():
            if patient_data['hospital_id'] == hospital_id:
                return patient_data
        return None
    
    def update_patient(self, phone: str, updated_data: Dict) -> bool:
        """Update existing patient data"""
        try:
            if phone in st.session_state.patients_db:
                st.session_state.patients_db[phone].update(updated_data)
                return True
            return False
        except Exception as e:
            st.error(f"Update error: {str(e)}")
            return False
    
    def get_total_patients(self) -> int:
        """Get total number of registered patients"""
        return len(st.session_state.patients_db)

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Simple validation for 10-digit phone numbers
    pattern = r'^\d{10}$'
    return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))

def generate_hospital_id() -> str:
    """Generate unique hospital ID"""
    return f"HSP-{str(uuid.uuid4())[:8].upper()}"

def render_patient_registration():
    """Render patient registration form"""
    st.markdown('<div class="section-header"><h3>🆕 New Patient Registration</h3></div>', 
                unsafe_allow_html=True)
    
    with st.form("patient_registration_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="Enter patient's full name")
            age = st.number_input("Age *", min_value=0, max_value=150, value=0)
            gender = st.selectbox("Gender *", ["", "Male", "Female", "Other"])
        
        with col2:
            phone = st.text_input("Phone Number *", placeholder="Enter 10-digit phone number")
            address = st.text_area("Address *", placeholder="Enter complete address")
        
        submitted = st.form_submit_button("Register Patient", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            errors = []
            if not name.strip():
                errors.append("Name is required")
            if age <= 0:
                errors.append("Valid age is required")
            if not gender:
                errors.append("Gender selection is required")
            if not phone.strip():
                errors.append("Phone number is required")
            elif not validate_phone(phone):
                errors.append("Please enter a valid 10-digit phone number")
            if not address.strip():
                errors.append("Address is required")
            
            if errors:
                for error in errors:
                    st.error(error)
                return
            
            # Check if patient already exists
            db = PatientDatabase()
            clean_phone = phone.replace('-', '').replace(' ', '')
            
            if db.get_patient_by_phone(clean_phone):
                st.error("📱 A patient with this phone number is already registered!")
                return
            
            # Create and save patient
            hospital_id = generate_hospital_id()
            patient = Patient(
                hospital_id=hospital_id,
                name=name.strip(),
                age=age,
                gender=gender,
                phone=clean_phone,
                address=address.strip()
            )
            
            if db.save_patient(patient):
                st.success("✅ Patient registered successfully!")
                st.markdown(f"""
                <div class="patient-card">
                    <h4>📋 Patient Details</h4>
                    <p><strong>Hospital ID:</strong> {hospital_id}</p>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Phone:</strong> {clean_phone}</p>
                    <p><em>Please save the Hospital ID for future reference</em></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ Failed to register patient. Please try again.")

def render_patient_lookup():
    """Render patient lookup and update form"""
    st.markdown('<div class="section-header"><h3>🔍 Patient Information Lookup</h3></div>', 
                unsafe_allow_html=True)
    
    # Search form
    with st.form("patient_search_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_type = st.radio("Search by:", ["Phone Number", "Hospital ID"], horizontal=True)
            if search_type == "Phone Number":
                search_value = st.text_input("Enter Phone Number", placeholder="Enter 10-digit phone number")
            else:
                search_value = st.text_input("Enter Hospital ID", placeholder="Enter Hospital ID (e.g., HSP-12345678)")
        
        with col2:
            search_submitted = st.form_submit_button("🔍 Search", type="primary", use_container_width=True)
    
    if search_submitted and search_value:
        db = PatientDatabase()
        
        # Search for patient
        if search_type == "Phone Number":
            clean_search = search_value.replace('-', '').replace(' ', '')
            if not validate_phone(clean_search):
                st.error("Please enter a valid 10-digit phone number")
                return
            patient_data = db.get_patient_by_phone(clean_search)
        else:
            patient_data = db.get_patient_by_id(search_value.upper())
        
        if patient_data:
            st.success("✅ Patient found!")
            
            # Update form
            st.markdown('<div class="section-header"><h4>📝 Update Patient Information</h4></div>', 
                        unsafe_allow_html=True)
            
            with st.form("patient_update_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    updated_name = st.text_input("Full Name", value=patient_data['name'])
                    updated_age = st.number_input("Age", min_value=0, max_value=150, 
                                                value=patient_data['age'])
                    updated_gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                                index=["Male", "Female", "Other"].index(patient_data['gender']))
                
                with col2:
                    updated_phone = st.text_input("Phone Number", value=patient_data['phone'])
                    updated_address = st.text_area("Address", value=patient_data['address'])
                
                # Display current info
                st.info(f"🆔 Hospital ID: **{patient_data['hospital_id']}**")
                
                update_submitted = st.form_submit_button("Update Patient Info", type="primary", 
                                                       use_container_width=True)
                
                if update_submitted:
                    # Validation
                    errors = []
                    if not updated_name.strip():
                        errors.append("Name is required")
                    if updated_age <= 0:
                        errors.append("Valid age is required")
                    if not updated_phone.strip():
                        errors.append("Phone number is required")
                    elif not validate_phone(updated_phone):
                        errors.append("Please enter a valid 10-digit phone number")
                    if not updated_address.strip():
                        errors.append("Address is required")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                        return
                    
                    # Update patient data
                    updated_data = {
                        'name': updated_name.strip(),
                        'age': updated_age,
                        'gender': updated_gender,
                        'phone': updated_phone.replace('-', '').replace(' ', ''),
                        'address': updated_address.strip()
                    }
                    
                    if db.update_patient(patient_data['phone'], updated_data):
                        st.success("✅ Patient information updated successfully!")
                        # Update the phone key if it changed
                        if updated_data['phone'] != patient_data['phone']:
                            # Remove old entry and add new one
                            del st.session_state.patients_db[patient_data['phone']]
                            updated_data['hospital_id'] = patient_data['hospital_id']
                            st.session_state.patients_db[updated_data['phone']] = updated_data
                            st.info("📱 Phone number updated. Please use the new number for future searches.")
                    else:
                        st.error("❌ Failed to update patient information. Please try again.")
        else:
            st.error("❌ Patient not found!")
            st.info("💡 **Suggestion:** The patient may need to be registered first. Please use the 'New Patient Registration' section.")

def render_sidebar():
    """Render sidebar with app info and statistics"""
    with st.sidebar:
        st.markdown("""
        ### 🏥 Hospital Management
        
        **Quick Guide:**
        - **Register** new patients with basic info
        - **Search** by phone or Hospital ID
        - **Update** patient information as needed
        """)
        
        db = PatientDatabase()
        total_patients = db.get_total_patients()
        
        st.markdown(f"""
        ### 📊 Statistics
        - **Total Patients:** {total_patients}
        """)
        
        if total_patients > 0:
            st.markdown("### 📋 Recent Registrations")
            # Show last 3 registered patients
            recent_patients = list(st.session_state.patients_db.values())[-3:]
            for patient in reversed(recent_patients):
                st.markdown(f"**{patient['name']}**  \n📱 {patient['phone']}")
        
        st.markdown("---")
        st.markdown("*Built with Streamlit*")

def main():
    """Main application function"""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Hospital Patient Management System</h1>
        <p>Streamline patient data entry across departments</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Main content tabs
    tab1, tab2 = st.tabs(["👤 Patient Registration", "🔍 Patient Lookup & Update"])
    
    with tab1:
        render_patient_registration()
    
    with tab2:
        render_patient_lookup()

if __name__ == "__main__":
    main()