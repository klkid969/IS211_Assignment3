import argparse
import csv
import re
import requests
import datetime

def download_file(url, filename):
    """Downloads a file from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        with open(filename, 'wb') as f: # Open file in binary write mode
            f.write(response.content) # Write the content from response to file
        print(f"Downloaded {filename} from {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        exit()

def process_log_file(filename, image_regex):
    """Processes the log file to analyze image requests and browser usage."""

    total_requests = 0
    image_requests = 0
    browser_counts = {}
    hourly_counts = {} # Extra Credit
    image_size = 0
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None) # Skip header
            for row in reader:
                if not row: #Skip empty rows
                    continue

                total_requests += 1
                # Extract data from the row (adjust indices if needed)
                path_to_file = row[0]  # Path to file
                timestamp_str = row[1]  # Timestamp (string)
                browser_info = row[2]  # Browser
                status_code = row[3]    # The row[3] is the status code of the request. 200 is a status code which means that the request is valid
                size_in_bytes = row[4]    # The row[4] is the size of the request in bytes

                # Part III: Image request analysis
                if re.search(image_regex, path_to_file, re.IGNORECASE):
                    image_requests += 1
                    image_size = image_size + int(size_in_bytes)

                #Part IV Browser Analysis

                # Extract browser from User-Agent
                browser = extract_browser(browser_info)
                if browser:
                    browser_counts[browser] = browser_counts.get(browser, 0) + 1

                # Parse timestamp
                timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')  # Format: "2014-01-27 00:00:01"
                hour = timestamp.hour

                # Extra Credit
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
                total_size_in_mb = image_size / (1024 * 1024)


        #Print image information
        image_percentage = (image_requests / total_requests) * 100
        print(f"Image requests account for {image_percentage:.1f}% of all requests")
        print(f"The total size of all image requests equals {total_size_in_mb:.1f} MB")


        # Print most popular browser
        most_popular_browser = max(browser_counts, key=browser_counts.get)
        print(f"The most popular browser is: {most_popular_browser}")

        #Extra Credit: Hourly Log Report
        print("\nHourly Log Report:")
        for hour, count in sorted(hourly_counts.items()):
            print(f"Hour {hour:02d} has {count} hits")



    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")

def extract_browser(user_agent_string):
  """Extracts the browser name from a User-Agent string."""
  if 'Firefox' in user_agent_string:
    return 'Firefox'
  elif 'Chrome' in user_agent_string:
    return 'Chrome'
  elif 'Safari' in user_agent_string and 'Chrome' not in user_agent_string:
    return 'Safari' # Safari must come before chrome because the safair check must be done first
  elif 'MSIE' in user_agent_string or 'Trident' in user_agent_string:
    return 'Internet Explorer'
  else:
    return 'Other'

def main():
    """Main function to parse arguments and process the log file."""
    parser = argparse.ArgumentParser(description="Analyze a web server log file.")
    parser.add_argument("--url", required=True, help="URL of the web log file.")
    args = parser.parse_args()

    filename = "weblog.csv"
    download_file(args.url, filename) #downloads file from URL
    image_regex = r"\.(jpg|gif|png)$" #regex to check if the row is an image or not
    process_log_file(filename, image_regex)

if __name__ == "__main__":
    main()
