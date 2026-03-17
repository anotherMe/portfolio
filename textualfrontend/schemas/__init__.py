"""
Schemas for the portfolio management application.

This module defines the Pydantic models used for data validation and serialization in the 
portfolio management application. These schemas represent the structure of data
sent between the frontend and backend, as well as the data returned by the API endpoints.

NOTE: actually this module is a copy of the one in the backend, but it is needed to avoid 
circular imports when importing the same schemas in both backend and frontend. In the future, 
we might want to split the schemas into separate files (e.g., portfolio.py, transactions.py) 
to avoid this duplication.

"""
