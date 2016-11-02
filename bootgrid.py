from flask import jsonify, request, g
from sqlalchemy import asc, desc, or_, types, text, case, and_
import sqlalchemy


class BootgridServerSide():
    """
    H1 -- Bootgrid Server Side Processing Base Class
    *************************************************

    You can call the base class on it's own to get basic functionality, or you can use it as a base and create a more specific usage case requireing more than the simple query and asociated generators.
    """

    def __init__(self, Request, Model):
        """
        H2 -- Bootgrid Server Side Constructor
        ***************************************

        Takes the user passed request object and database model to use,the constructor also defines variables with default values so valid result is always returned.
        """
        self.where = text( " 1=1 " )
        self.order_by = text( "" )
        self.rows = 10 # Number of rows to show by default
        self.current = 1 # Current Page
        self.model = Model
        self.request = Request

    def SortData(self):
        """
        H2 -- Bootgrid Sorting
        ***********************

        Sorting is setup in this function no direct calls to the database are made in this function. Some replacing is neccesary to deal with the way bootgrid sends it's sort parameters.
        """
        if self.request.form:
            params = self.request.form
            for key in params:
                # Bootgrid sends the sort field as "sort[first_name]: asc"
                if key.startswith('sort'):
                    sort_field = ''
                    sort_field = key.replace('sort[', '').replace(']', '')
                    sort_order = 'asc' if params[key] == 'asc' else 'desc'
                    sort_field = getattr(self.model, sort_field)
                    if sort_order == 'desc':
                        sort_field = desc(sort_field)
                    else:
                        sort_field = asc(sort_field)
                    self.order_by = sort_field



    def SearchData(self):
        """
        H2 -- Bootgrid Searching
        *************************

        Search is created is a similar way to sort so the function itself does not run any querys just creates an expresion to be run later. Only text fileds are searched by checking column types this stops issues with meta send with the request.
        """
        if self.request.form['searchPhrase']:
            search_phrase = self.request.form['searchPhrase']
            search_expr = '%' + '%'.join(search_phrase.split()) + '%'

            filters = []
            for field in self.model.__table__.columns.keys():
                column = getattr(self.model, field)
                # NOTE only text fields are searched
                if isinstance(column.type, types.String):
                    like = getattr(column, 'ilike')
                    filters.append(like(search_expr))

            if len(filters) > 0:
                filter_expr = filters.pop()
                filter_expr = reduce(lambda filter_expr, filter: or_(filter_expr, filter), filters, filter_expr)
            self.where = filter_expr

    def RowCount(self):
        """
        H2 -- Bootgrid Set Row Count
        *****************************

        Sets the row count sent by bootgrid if it is not sent the default of 10 is used instead. The function casts the data direct from the request to an int as it is sent as a string.
        """
        if self.request.form['rowCount']:
            self.rows = int(request.form['rowCount'])

    def HighLowLimit(self):
        """
        H2 -- Bootgrid Page Number
        ***************************

        Sets the current page for the pagination part of the query to increase efficency only having to get part of data making results much quicker to load.
        """
        if self.request.form['current']:
            self.current = int(request.form['current'])

    def JsonResponse(self):
        """
        H2 -- Bootgrid Query Execute and Jsonify
        *****************************************

        Runs the base query that returns all data from the model but allows for filtering and searching of the database. A count of the total number of records is got and then all data is formated for json encoding ready for bootgrid.
        """
        row2dict = lambda r: {c.name: getattr(r, c.name) for c in r.__table__.columns}

        count = self.model.query.count()
        rowsList = []

        result = self.model.query.filter(self.where).order_by(self.order_by).paginate(page=self.current, per_page=self.rows, error_out=True)
        for page in result.items:
            rowsList.append(row2dict(page))

        json = {'current': self.current, 'rowCount': self.rows, 'rows': rowsList, 'total': count}
        return jsonify(json)
