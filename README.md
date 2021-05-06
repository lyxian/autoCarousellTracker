# AutoCarousellTracker

Current Build/Branch:

- first/second : 2x Worker
- v7 : Zapier-Web

Requirements:

- gspread
- oauth2client
- pandas
- cryptography

## Changelogs

- v1 : Added settings + Able to handle multiple queries
- v2 : Added "exclude keywords" functionality + Changed "update-all" interval from 8 -> 3 hours
- v3 : Moved "update" after "results search" + Improved accuracy of results (index didn't change after exclusion)
- v4 : Improved accuracy of delay (minus runtime from delay) + Included updates for "other" sheets
- v5 : Added on/off button
- v6 : Added "meet-up" column + Main code refactoring + Added ENV

## Improvements

- "update-all" for top/lastest \_ listings
- integrate with Telegram/Slack
- add script to automate setup
- (at v3) new listing status updates immediately (wait an hour previously) <- Resolved
- (v6) breaking down main code + add "meet-up" column + client_secret & key in ENV
- (v7b) alternating workers to distribute dyno hours

## Bugs / Non-Bugs

### New

- exceptions raised not reflected if code exits early
- data migration in DB due to column changes

### Old

- bug (inaccurate updates) -> added "reset_index"
- non-bug (update-all start time increases everytime) -> get_results first than updates (!! won't work) <- deduct update-time from DELAY
- need to update '-' in non-queried sheets

### V6

- location APIs :
  - api.bigdatacloud > reverse-geocode-client
  - geocode.xyz
  - onemap.gov.sg

### V7b (switch app via API)

- create heroku credentials
- test API
- test sample code
- deploy (consider cross-account operations)
