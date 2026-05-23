# I have retructure and put all the strating steps here for project to run.
alembic init migrations
alembic upgrade head && uvicorn app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]