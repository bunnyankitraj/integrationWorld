1. Install all dependencies using pip:
   pip install -r requirements.txt

2. Run the development server:
   python manage.py runserver

3. Working API (Convert XML to JSON) — Example using `curl`:

   curl --location 'http://localhost:8000/process_json/' \
   --header 'Content-Type: application/json' \
   --data '{
       "num1": 10,
       "num2": 50
   }'
