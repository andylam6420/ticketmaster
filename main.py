""" IMPORT PACKAGES AND LIBRARIES """
try:
    # Standard libraries
    import argparse
    import datetime
    from dateutil.relativedelta import relativedelta
    import json
    import smtplib, ssl                                             # Email libraries
    from getpass import getpass                                     # password library
    from apscheduler.schedulers.blocking import BlockingScheduler   # Scheduling library

    # APIs
    import ticketpy

except Exception as e:
    print("Some modules are missing: {}".format(e))


""" GLOBAL VARIABLES """
tm_client = ticketpy.ApiClient('8cEwqGArfXQASWA5eTzI506FGDCkYDkc')  # TicketMaster API Key


""" TICKETMASTER AUTO MAIN """
def main(args):

    results = None
    # EVENT QUERIES
    if (args.event):
        results = eventSearch()
    
    # VENUE QUERIES
    if (args.venue):
        results = venueSearch()

    # ATTRACTION QUERIES
    if (args.attraction):
        results = attractionSearch()

    # CLASSIFICATION (GENRE) QUERIES
    if (args.classification):
        results = classificationSearch()

    # Email results to personal email
    emailResults(results)



def emailResults(results):
    port = 465  # For SSL
    email = input("Enter your personal email address: ")
    password = getpass("Enter email address password: ")

    message = """\
    Subject: Your TicketMaster Search Results\n
""" + results

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Send email helper function which is called by daemon process
    def sendEmail():
        print("Sending search results to " + email + "...")
        server.sendmail(email, email, message)

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email, password)

        print("TicketMaster sleeping before sending email")

        # Set timer
        scheduler = BlockingScheduler()
        scheduler.add_job(sendEmail, 'interval', minutes=1)
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
                raise ValueError
        except ValueError:
            print("Please enter a valid state abbreviation.")
            continue
        else:
            break
    
    # Radius adjust
    while True:
        try:
            radius = str(int(input("Radius of area to search: ")))
        except ValueError:
            print("Please enter a valid radius number.")
            continue
        else:
            break
    
    # Radius unit adjust
    units = { "m" : "miles", "km" : "km" }
    while True:
        try:
            unit = input("Unit of radius (\'m\' or \'km\'): ")
            
            if unit not in units:
                raise ValueError
        except ValueError:
            print("Please enter a valid radius number.")
            continue
        else:
            unit = units[unit]
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
            time = input("Time search duration from now: ")
            
            if time not in time_duration:
                raise ValueError
        except ValueError:
            print("Please enter a valid radius number.")
            continue
        else:
            time = time_duration[time]
            break


    # Response size
    while True:
        try:
            size = str(int(input("Up to how many results would you like? ")))
        except ValueError:
            print("Please enter a valid response size.")
            continue
        else:
            break

    # Search result sorting
    sort_filter = {'', 'name,asc', 'name,desc', 'date,asc', 'date,desc', 'relevance,asc', 'relevance,desc', 'distance,asc', 'name,date,asc', 'name,date,desc', 'date,name,asc', 'date,name,desc', 'distance,date,asc', 'onSaleStartDate,asc', 'id,asc', 'venueName,asc', 'venueName,desc', 'random'}
    print("Here is a list of possible sorting options:")
    
    print("""
    name (ascending order)       : name,asc
    name (descending order)      : name,desc
    date (ascending order)       : date,asc
    date (descending order)      : date,desc
    relevance (ascending order)  : relevance,asc
    relevance (descending order) : relevance,desc
    distance (ascending order)   : distance,asc
    venue name (ascending order) : venueName,asc
    venue name (descending order) :venueName,desc
    """)

    while True:
        try:
            sort = input("Would you like to sort? If yes, type in an above sorting option: ")
            
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
    
    # GET Event Search TicketMaster Discovery API call
    event_dao = tm_client.events
    pages = event_dao.find(
        keyword=keyword,
        state_code=state_code,
        radius=radius,
        unit=unit,
        start_date_time=current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        end_date_time=(current_time + time).strftime("%Y-%m-%dT%H:%M:%SZ"),
        size=size,
        sort=sort
    ).one()

    results = str()
    # Print out Event search results
    for event in pages:
        results += str(event) + "\n"
    
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='PROG', usage='%(prog)s [options]')
    parser.add_argument('-e', '--event', action='store_true', help="Find events and filter your search by location, date, availability, and much more")
    parser.add_argument('-v', '--venue', action='store_true', help="Find venues and filter your search by name, and much more")
    parser.add_argument('-a', '--attraction', action='store_true', help="Find attractions (artists, sports, packages, plays and so on) and filter your search by name, and much more")
    parser.add_argument('-c', '--classification', action='store_true', help="Find classifications and filter your search by name, and much more. Classifications help define the nature of attractions and events")
    
    main(parser.parse_args())