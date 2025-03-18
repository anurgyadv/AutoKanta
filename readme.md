# Dharam Kanta Automation System

## Background

The Dharam Kanta Automation System aims to modernize traditional weighing bridges by eliminating manual data entry. Currently, weighing bridge operators must manually type driver and vehicle information into their systems, which is time-consuming and prone to errors. Our solution bridges the gap between online forms and legacy weighing software.

## Current Implementation

- **Digital Form Access**: Drivers scan a QR code to access a Google Form
- **Data Collection**: Form collects vehicle registration, driver details, cargo information
- **Backend Integration**: Form submissions stored in Google Sheets
- **Automation Layer**: Raspberry Pi configured as USB keyboard monitors for new submissions
- **Automated Input**: Pi automatically inputs form data into weighing machine software

The system uses a Raspberry Pi that acts as a USB keyboard, typing the information submitted through online forms directly into the weighing bridge software. This eliminates manual data entry while allowing continued use of existing weighing software.

## Future Steps

### Short-term
- Improve error handling and recovery mechanisms
- Add basic validation for form inputs
- Create simple status monitoring system

### Medium-term
- Implement UPI payment instructions in the form
- Develop payment verification system
- Create admin dashboard for monitoring system status

### Long-term
- Full integration with payment gateways for automatic verification
- Mobile app for drivers with additional features
- Data analytics for weighing patterns and efficiency improvements

---

*This project is currently in active development*
