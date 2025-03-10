# This is the beginning of automating a Dharam Kanta, based on a web form for drivers.


Workflow as of now :
1. Driver scans a QR, reaches a google form.
2. Payment is done with UPI with address provided on the webform. (Payment part would be added much later in the future.)
3. Once Payment is validated using some UPI API (Assuming one exits, if not we will work out some other way)
4. The driver will fill a form, which will have all the required questions.
5. The raspberry pi (Connected to machine), runs a script which detects any new entries in the form.
6. Use these entries, to input them into the machine and prints the final reciept.

The raspberry pi here will be functioning as an automated keyboard.

More to follow.
