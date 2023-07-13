- Initial observations:
    - We have 21310 rows, 7 columns in total;
    - We don't know for now what our target variable, but I'm going to suppose it is the timedelta;
    - We have 2 int, 2 obj and 3 float columns. If we don't take the ids into consideration, we are left with 2 cat variables and 3 numerical variables;
    - We have some missing values in the delay_at_checkout_in_minutes column (23%) and significantly more missing values in the previous_ended_rental_id and time_delta columns (91%). However, due to the explination presented in the dataset key, we can suppose that the missing values have some signification, so for now we will not consider dropping them;
    - We can notice that for our two categorical variables, checkin_type and state, mobile and ended categories are clearly the dominant categories respectively;
    - By observing the canceled category in the state column, we can find only one not null value. We think that the delay is only considered for the ended state category. Potentially, we might focus on only those cases as they are the cases to be studied;

- In depth analysis
    - By separating our data into ended and canceled, we can see that most values in delay column are NaN for the canceled rentals. We can't explain if these NaN values have any signification. (e.g:an error in the data collection process, the time delta was so large the rental got cancelled automatically);
    - Numerical variables analysis:
        - the box plots show a large number of outliers in the delay column, some outliers in the previous_ended column
    - Categorical variables analysis:
        - As we saw earlier, the mobile and ended are the dominating categories for each column respectively
        - Also, we have 8101 unique car ids, so that means we have 8101 potentially unique client.
    - Target variable analysis:
        - We created a new target variable column, called 'delay_category' where we have a category per delay intervals: no delay, delay < 30 minutes, 30 minutes <= delay < 1 hour, 1 hour <= delay < 2 hours, 2 hours <= delay


- Target variable:
    - By exploring the 'delay_category' column, we find 54.1% of the total rentals have been delayed, however does these delays actually affect the next trip ? 

- Target/features analysis:
    - Since most of the checkin types are mobile, the most affected are indeed the mobile category. By looking at the proportions, we do see that the connect has less delay proportionally to the mobile checkin type.
    - The time-delta seems pretty similar relatively to the delay categories
    - On average, delay is around 80 mins for connect rentals and 224 mins for mobile rentals
    - Also, on average, time delta is around 260 mins for both rentals and mobile rentals
    - We create two additional columns, real_time_delta and waited for rental:
        - real_time_delta is the real time between rentals, delay included
        - and waited_for_rental checks if the driver did wait or not for his rented car to arrive from the previous rental
        - we create these two columns, for the delay and delay_true datasets
        - 