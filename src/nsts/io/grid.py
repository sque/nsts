'''
Created on Nov 6, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

class ColumnDescriptor(object):
    
    def __init__(self, title, width, align):
        self.width = width
        self.title = title
        
        assert align in ['left', 'right', 'center']
        alignsymbol_hasmap = {'left' : '<', 'center' : '^', 'right' : '>'}
        self.align = align
        self.align_symbol = alignsymbol_hasmap[self.align]

class Grid(object):
    pass
    
    def __init__(self, width):
        self.width = width
        self.column_descriptor = []
        self.rows = []
        
    def add_column(self, title, width = 'equal', align = 'left'):
        '''
        Width can be 'equal', 'fit' or number.
        - equal: will split space equally with other equal columns
        - fit: will expand to fit all data
        - number: a fixed width in number of characters
        Align can be 'left', 'right' or 'center'
        '''
        self.column_descriptor.append(ColumnDescriptor(title = title, width = width, align = align))
        
    def add_row(self, row):
        assert isinstance(row, list)
        self.rows.append(row)
        
    def get_column_widths(self):
        '''
        It will return whitespace (without column delimiters)
        '''
        
        column_widths = [c.width for c in self.column_descriptor]
        for i, c_width in enumerate(column_widths):
            if c_width == 'fit':
                column_widths[i] = -1
                column_widths[i] = max([len(str(row[i])) for row in self.rows])
        
        # Calculate space that is fixed
        fixed_space = sum([w for w in column_widths if w is not 'equal'])
        fixed_space += (len(self.column_descriptor) - 1) * 3 + 2    # Space used by cell delimiters

        # Calculate equal space
        total_equal = column_widths.count('equal')
        equal_cell_width = int(self.width - fixed_space) // total_equal
        
        # Find error from rounding and append to the first column
        extra_padding = self.width - (fixed_space + (equal_cell_width * total_equal))
        for i, c_width in enumerate(column_widths):
            if c_width == 'equal':
                column_widths[i] = extra_padding + equal_cell_width
                extra_padding = 0

        return column_widths
    
    def __render_split_row(self, column_widths):
        
        output = "+-"
        for i, cwidth in enumerate(column_widths):
            output += "{0:-<{width}}".format("", width = cwidth)
            if i != len(column_widths) - 1:
                output += "-+-"
        output += "-+"
        return output
    
    def __render_row(self, row, column_widths):
        
        row_data = [str(cell).strip() for cell in row]
        # This variable will be populated with an extra row
        # if data does not fit
        extra_row = None
        
        output = "| "
        for i, cwidth in enumerate(column_widths):
            
            # Split in multiple rows if cell does not fit
            if len(row_data[i]) > cwidth:
                # If this is the first multiline cell, initialize next row
                if extra_row is None:
                    extra_row = [""] * len(column_widths)
                # Split data to current row and next row(s)
                extra_row[i] = row_data[i][cwidth:]
                row_data[i] = row_data[i][:cwidth]
                
            # Format cell
            output += "{0: {align}{width}}".format(
                    row_data[i],
                    width = cwidth,
                    align = self.column_descriptor[i].align_symbol)
            if i != len(column_widths) - 1:
                output += " | "
        output += " |"
        
        # Recursively populate extra rows
        if extra_row:
            output+=  "\n" + self.__render_row(extra_row, column_widths)
        return output
    
    def render(self):
        if not self.column_descriptor:
            raise RuntimeError("Cannot create a grid with no columns")
        
        column_widths = self.get_column_widths()
        output = ""
        
        
        output += self.__render_split_row(column_widths) + "\n"
        
        # Render titles
        titles = [str(c.title) for c in self.column_descriptor]
        title_max_size = max([len(t) for t in titles])
        if title_max_size:
            output += self.__render_row(titles, column_widths) + "\n"
            output += self.__render_split_row(column_widths) + "\n"
        
        # Render data
        for row in self.rows:
            output += self.__render_row(row, column_widths) + "\n"
        output += self.__render_split_row(column_widths)
        return output

    def __repr__(self):
        return self.render()

    def __str__(self):
        return self.render()

if __name__ == "__main__":
    
    g = Grid(80)
    g.add_column('', 'fit', 'center')
    g.add_column('Description', 'equal')
    g.add_column('Extra', 'equal',)
    g.add_column('', 1, )
    g.add_row([1,'Something ', 'Sadomina otipisera potsoures', 'X'])
    g.add_row([2,'More Here', 'Ravidamina osekeme taloupa', ''])
    g.add_row([33,'Lolalila', 'Abraoumba outeke mesa remi', ''])
    g.add_row([44,'Ooxoxoxox', 'Tersamer blame douke', 'X'])
    g.add_row([105,'Lorium bla oubmla oukek ketestesra ramanina', 'Got it?', 'X'])
    print g
    
    g = Grid(60)
    g.add_column('', 'fit', 'left')
    g.add_column('Left', width='equal', align='left')
    g.add_column('Right', width='equal', align='right')
    g.add_column('Center', width= 15 , align='center')
    g.add_row([1,'Something ', 'Sadomina ', 'potsoures'])
    g.add_row([2,'More Here', 'Ravidamina', 'taloupa'])
    g.add_row([33,'Lolalila', 'Abraoumba', 'remi'])
    g.add_row([44,'Ooxoxoxox', 'Tersamer',' douke'])
    g.add_row([105,'Lorium bla','ramanina', 'Got it?'])
    print g