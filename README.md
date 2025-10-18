We are building a web app for youtubers and youtube users. They paste URL of one video, and will be able to view a report of that video's comment section. Youtubers can also paste their youtube information and profile page in Personalization center for influence building suggestions.

The web app should include:

1. Comment scraper: able to pull large scale (e.g. 10k comments) data from youtube comment section.

automatically load comment scraper's data to comment analysis;

2. Comment analysis:

connect API, import scraper's data to AI.
AI need to: answer basic info << pull information from URL 
            use scraper's data to finish labeling, categorization, and output data for visualization

    Basic Info
        How many comments?
        How long is the video?
        How long has the video posted?
        What is the video mainly about?
        Show the trends of comments from time scale 
            Two perspective must include in this chart:
            e.g.0.2.1 2018 = 10 comments,2019 = 320 comments,2020 = 1320 comments (line chart)
            2.g.0.2.2 2018 + 10 comments,2019 + 310 comments,2020 + 1000 comments (bar chart)

    Three examples
        e.g.1 in a political video, there are people talking about "democrats vs republicans", "China", "Racism", "Immigrants", "Donald Trump"  
        e.g.2 in a cooking video, there are people talking about "love", "follow up", "hate".
        e.g.3 in a educational video, there are people talking about "quant careers", "people in quants", "wealth"

    Label these comments by their factors:
        e.g.3.1 "Quant people are all asian nerds." --> This commment discuss about #people, #quant, #ethinicity, #career, #socialperformance #peopleinquant #quantcareers
        e.g.2.1 "This is not real italian food, it's french!" --> This comment talks about #food, #foodorigin, #country, #french, #italian, #frenchanditalian 
        e.g.1.1 "Donald Trump is so egotistic. He being a president is no good for USA." --> This commment shows #USAPresident, #politics, #DonaldTrump, #personality, #personalitydisorder
        
        The rule of labeling:
            General rules: fore example, #food, #politics, #career, #people
            Specific rules: for example, #peopleinquant, #DonaldTrump 
            Sentiment analysis: #positive #negative #neutral
        
        Prioritization of labels:
            General rules are used for for general categorization, visualized in final output as pie chart.
            If comments related to a specific topic appeared in over 35% of comment section, then include this specific topic in the pie chart with general rules.
            Sentiment analysis have
            
    Categorize these commments by labels:
        What are each categories discussing about?
            e.g.1 output should be: 
                People in e.g.1 videos are talking about:
                    "democrats": 1299 comments, 28% holds positive attitude, 42% holds negative attitude, 30% holds neutral attitude
                    "republicans": 1299 comments, 72% holds positive attitude, 28% holds negative attitude
                    "China": 82 comments, 40% holds positive attitude, 45% holds negative attitude, 15% holds neutral attitude
                    "Racism": 190 comments, 21% holds positive attitude, 79% holds negative attitude
                    "Immigrants": 404 comments, 23% holds positive attitude, 77% holds negative attitude
                    "Donald Trump": : 2217 comments, 38% holds positive attitude, 62% holds negative attitude

        Among each topics:
            How many comments are positive, and how many are negative? 
                Use sentiment analysis
                e.g.3.1. "Quantitative analysis is a highly competitive and interesting job" vs "Quant is tiring"
                e.g.3.2. "Quant people are intelligence and rich" vs "Quant people are all asian nerds."
            What is the controversy rate?
                num_reply_in_stack = the amount of comment in the video that has over 100 replies
                controversy rate = (num_reply_in_stack / num_all_comments) * 100%

3. Visualization

automatically import data from comment analysis

definition: pie chart represent percentage, bar chart represent numbers, and line chart represent trends, unless claimed otherwise.

Call: 
    Basic Info 
        Comment numbers
        Video length
        Video post date
        Video main content
        Trends of comments from time scale 
            Two perspective must include in this chart:
            e.g.0.2.1 2018 = 10 comments,2019 = 320 comments,2020 = 1320 comments (line chart)
            2.g.0.2.2 2018 + 10 comments,2019 + 310 comments,2020 + 1000 comments (bar chart)
    Categories 
        What are each categories discussing about? in pie chart
        Categories' comments number in bar chart
        Each categories' comment attitude in pie chart with numbers of comments
        Each categories' controversy rate
                