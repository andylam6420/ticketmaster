""" IMPORT PACKAGES AND LIBRARIES """
try:
    # Standard libraries
    import argparse
    import datetime
    from dateutil.relativedelta import relativedelta
    import json
    from apscheduler.schedulers.blocking import BlockingScheduler   # Scheduling library

    import smtplib, ssl                                             # Email libraries
    from getpass import getpass                                     # password library
    from email.mime.text import MIMEText                            # Fancy email library
    from email.mime.multipart import MIMEMultipart                  # Fancy email library

    # APIs
    import ticketpy

except Exception as e:
    print("Some modules are missing: {}".format(e))


""" GLOBAL VARIABLES """
tm_client = ticketpy.ApiClient('8cEwqGArfXQASWA5eTzI506FGDCkYDkc')  # TicketMaster API Key


""" TICKETMASTER AUTO MAIN """
def main(args):

    # EVENT QUERIES
    if (args.event):                # If -e is passed as an argument in command line, run eventSearch()
        results = eventSearch()
    
    # VENUE QUERIES
    if (args.venue):                # If -v is passed as an argument in command line, run venueSearch()
        results = venueSearch()

    # ATTRACTION QUERIES
    if (args.attraction):           # If -a is passed as an argument in command line, run attractionSearch()
        results = attractionSearch()

    # CLASSIFICATION (GENRE) QUERIES
    if (args.classification):       # If -c is passed as an argument in command line, run attractionSearch()
        results = classificationSearch()

    # Email results to personal email
    emailResults(results)



def emailResults(results):

    # Get personal email and password from user
    email = input("Enter your personal email address: ")
    password = getpass("Enter email address password: ")

    # Create message Subject, specify sender email and receiver email
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your TicketMaster Search Results"
    message["From"] = email
    message["To"] = email
    
    # Text message of email
    text = results

    # Turn message into plain text object
    plain = MIMEText(text, "plain")

    # Convert plain text object into email
    message.attach(plain)

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Send email helper function which is called by daemon process
    def sendEmail():
        print("Sending search results to " + email + "...")
        server.sendmail(email, email, message.as_string())

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server: # Sets up email server (python standard library)
        server.login(email, password)   # login into your email

        print("TicketMaster sleeping before sending email")

        # Schedule email to be sent every 1/6th of a minute
        scheduler = BlockingScheduler()
        scheduler.add_job(sendEmail, 'interval', minutes=1/6)
        scheduler.start()


def eventSearch():
    ''' EVENT SEARCH 
    
    Find events and filter your search by location, date, availability, and much more.
    '''
    
    print("TICKET MASTER EVENT SEARCH", end="\n\n")

    # Keyword search
    keyword = input("Search for keyword: ")
    
    # State search
    states = { 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
           'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
           'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
           'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
           'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'}
    
    while True:
        try:
            state_code = input("Search by state (ex: \'CA\' not \'California\'): ").upper()
            
            if state_code not in states:
                raise ValueError            # when ValueError is raised, execute except block
        except ValueError:
            print("Please enter a valid state abbreviation.")
            continue
        else:
            break
    
    # Radius adjust
    while True:
        try:
            radius = str(int(input("Radius of area to search: ")))  # if input is not a number, integer conversion can't happen. ValueError will be raised.
        
            if int(radius) < 0:
                raise ValueError
        except ValueError:
            print("Please enter a valid radius number.")
            continue
        else:
            break
    
    # Radius unit adjust
    units = { 
        "m" : "miles", 
        "km" : "km" 
    }  # Dictionary of units
    
    while True:
        try:
            unit = input("Unit of radius (\'m\' or \'km\'): ")
            
            if unit not in units:
                raise ValueError
        except ValueError:
            print("Please enter a valid radius number.")
            continue
        else:
            unit = units[unit]      # takes user input as key, converts 'm' to 'miles' and 'km' to 'km' as value
            break

    # Time search duration
    current_time = datetime.datetime.now()

    time_duration = {
        "6 hours" : datetime.timedelta(hours=6),
        "12 hours" : datetime.timedelta(hours=12),
        "day" : datetime.timedelta(days=1),
        "week" : datetime.timedelta(days=7),
        "two week" : datetime.timedelta(days=14),
        "month" : relativedelta(months=1)
    }

    print("Here is a list of possible time search duration options from now:")
    
    print("""
    6 hours
    12 hours
    day
    week
    two week
    month
    """)

    while True:
        try:
            time = input("Choose a time frame you would like events to be searched within: ")
            
            if time not in time_duration:
                raise ValueError
        except ValueError:
            print("Please enter a valid time frame.")
            continue
        else:
            time = time_duration[time]
            break


    # Number of events to be notified to user in an email
    while True:
        try:
            size = str(int(input("Up to how many results would you like? ")))
            
            if int(size) < 0:
                raise ValueError
        except ValueError:
            print("Please enter a valid response size.")
            continue
        else:
            break

    # Search result sorting
    sort_filter = {'', 'name,asc', 'name,desc', 'date,asc', 'date,desc', 'relevance,asc', 'relevance,desc', 'distance,asc', 'name,date,asc', 'name,date,desc', 'date,name,asc', 'date,name,desc', 'distance,date,asc', 'onSaleStartDate,asc', 'id,asc', 'venueName,asc', 'venueName,desc', 'random'}
    print("Here is a list of possible sorting options:")
    
    print("""
    name (ascending order)          : name,asc
    name (descending order)         : name,desc
    date (ascending order)          : date,asc
    date (descending order)         : date,desc
    relevance (ascending order)     : relevance,asc
    relevance (descending order)    : relevance,desc
    distance (ascending order)      : distance,asc
    venue name (ascending order)    : venueName,asc
    venue name (descending order)   : venueName,desc
    """)
    
    # name (ascending order) - first event emailed to user is first alphabetically

    while True:
        try:
            sort = input("Would you like to sort (Ex. \"date,asc\")? By default, sorting order will be by date (ascending): ")
            
            if sort not in sort_filter:
                raise ValueError
        except ValueError:
            print("Please enter a valid sorting option.")
            continue
        else:
            if sort == '':
                sort = 'date,asc'
            break


    print("\nSearching for events...", end="\n\n")
    print("...")
    print("...")
    print("...")

    # GET Event Search TicketMaster Discovery API call
    event_dao = tm_client.events #Database access object for events
    
    pages = event_dao.find(
        keyword=keyword,        # Passing in user input data into Ticketmaster API call
        state_code=state_code,
        radius=radius,
        unit=unit,
        start_date_time=current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        end_date_time=(current_time + time).strftime("%Y-%m-%dT%H:%M:%SZ"),
        size=size,
        sort=sort
    ).one()

    results = ""                        # results is set to empty string
    # Print out Event search results
    for event in pages:
        results += str(event) + "\n"    # add each event converted as a string to results variable
    
    return results


def venueSearch():
    ''' VENUE SEARCH 
    
    Find venues and filter your search by name, and much more
    '''

    venue_dao = tm_client.venues
    venues = venue_dao.find(keyword="Tabernacle").all()
    for v in venues:
        print("Name: {} / City: {}".format(v.name, v.city))


def attractionSearch():
    ''' ATTRACTION SEARCH 
    
    Find attractions (artists, sports, packages, plays and so on) and filter your search by name, and much more.
    '''

    attraction_dao = tm_client.attractions


def classificationSearch():
    ''' CLASSIFICATION SEARCH 
    
    Find classifications and filter your search by name, and much more. Classifications help define the nature of attractions and events.
    '''

    classification_dao = tm_client.classifications


# Main block which starts the program and enables passing in arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='PROG', usage='%(prog)s [options]')
    parser.add_argument('-e', '--event', action='store_true', help="Find events and filter your search by location, date, availability, and much more")
    parser.add_argument('-v', '--venue', action='store_true', help="Find venues and filter your search by name, and much more")
    parser.add_argument('-a', '--attraction', action='store_true', help="Find attractions (artists, sports, packages, plays and so on) and filter your search by name, and much more")
    parser.add_argument('-c', '--classification', action='store_true', help="Find classifications and filter your search by name, and much more. Classifications help define the nature of attractions and events")
    
    main(parser.parse_args())