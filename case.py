import numpy as np
import matplotlib.pyplot as plt

"""
# SUMMARY #
A script that attempts to solve the "Real Problems We Tackle: Pricing #1"(https://creatingvalue.substack.com/p/real-problems-we-tackle-pricing-level)
problem. This script outputs a matplotlib plot that maps out the costs of user and driver acquisition as well as the revenue breakdown. Some aspects
of the problem were simplified to make this script more of a calculation than a simulation (see IGNORED DETAILS).

# ASSUMPTIONS ##
1) number of drivers on the app stays constant each month
2) number of users stays the same each month, number of users lost = number of users acquired each month
3) user acquisition costs have an inverse relationship with the number of users being acquired

# IGNORED DETAILS #
"but riders who experience one or more “failed to find driver” events churn at 33% monthly"
- I ignored the "one or more" aspect of this for simplification. User churn would likely be slightly higher over the
  long run since each user that experiences a failed match would then forever have a 33% chance of churn. Instead
  I assumed that for a given month where a user has a failed match they churn at 33%. This keeps the calculation stateless
  between months, so that I don't have to keep track of how many users fail to match but don't churn each month
"""

## CONSTANTS: given & assumptions ##
trip_rate = 25                                                      #GIVEN: "Let’s assume that you cannot charge riders more than the prevailing rate [of $25]"
initial_num_users = 1000                                            #ASSUMPTION: number of users in a month is constant
driver_trips_per_month = 100                                        #GIVEN: "drivers ... complete 100 rides / month"
user_rides_per_month = 1                                            #GIVEN: "Each rider requests 1 ride / month on average"
initial_num_drivers = initial_num_users/driver_trips_per_month      #ASSUMPTION: number of drivers exactly meets the needs of the number of users
driver_churn = 0.05                                                 #GIVEN: "drivers have a 5% monthly churn rate"
rider_failed_match_churn = 0.33                                     #GIVEN: "riders who experience ... “failed to find driver” events churn at 33% monthly"
rider_success_match_churn = 0.1                                     #GIVEN: "riders who don’t experience a “failed to find driver” event churn at 10% monthly"


#----------------------------------------------------------#
## ROUND TO NEAREST CENT HELPER FUNCTION ##
def round_to_nearest_cent(value):
    """round a decimal value to its nearest cent (0.01)

    Args:
        value (float): a decimal value representing a dollar amount

    Returns:
        float: rounded decimal value to nearest cent
    """
    return round(value*100)/100


#----------------------------------------------------------#
## CALCULATING USER RELATED COSTS ##

## SETTING COEFFICIENTS FOR USER ACQUISITION COST vs NUM USERS ACQUIRED
# y = 10/x + 10
# y = 20 @ x = 1
# limit of y as x approaches infinity = 10
user_a = 10
user_b = 10

def user_cost(users_added):
    """ufunc numpy function for calculating user acquisition cost

    Args:
        users_added (int): number of users added

    Returns:
        float: cost to add a user @ users_added
    """
    return user_a/users_added + user_b

def calculate_user_acquisition_cost(users_added):
    """calculate cost to acquire lost users for a numpy array

    Args:
        users_added (int[]): an array with the number of users needed to be acquired

    Returns:
        float[]: an array of the cost to acquire given number of users
    """
    user_cost_func = np.frompyfunc(user_cost, 1, 1)

    acquisition_cost_per_user = user_cost_func(users_added)
    print(acquisition_cost_per_user)

    return users_added * acquisition_cost_per_user

#----------------------------------------------------------#

## CALCULATING DRIVER RELATED COSTS ##

## SETTING COEFFICIENTS FOR USER ACQUISITION COST vs NUM USERS ACQUIRED
# y = 200/x + 400
# y = 600 @ x = 1
# limit of y as x approaches infinity = 400
driver_a = 200
driver_b = 400

def driver_cost(drivers_added):
    """ufunc numpy function for calculating driver acquisition cost

    Args:
        drivers_added (int): number of drivers added

    Returns:
        float: cost to add a driver @ drivers_added
    """
    return driver_a/drivers_added + driver_b

def calculate_driver_acquisition_cost(drivers_added):
    """calculate cost to acquire lost drivers for a numpy array

    Args:
        drivers_added (int[]): an array with the number of drivers needed to be acquired

    Returns:
        float[]: an array of the cost to acquire given number of drivers
    """
    driver_cost_func = np.frompyfunc(driver_cost, 1, 1)

    acquisition_cost_per_driver = driver_cost_func(drivers_added)
    print(acquisition_cost_per_driver)

    return drivers_added * acquisition_cost_per_driver

#----------------------------------------------------------#

## CALCULATING POSITIVE MATCH RATE FROM LINEAR RELATIONSHIP WITH LYFT TAKE ##

## SETTING LINEAR COEFFICIENTS FOR MATCH RATE VS LYFT TAKE
x = np.array([3,6])
y = np.array([0.93, 0.6])
coefficients = np.polyfit(x, y, 1)

def positive_match_from_lyft_take_linear(lyft_take):
    # find linear coefficients
    # ASSUMPTION: relationship between positive match and lyft take is linear

    new_y = coefficients[0]*lyft_take + coefficients[1]
    new_y = np.minimum(1.0, new_y)
    new_y = np.maximum(0.0, new_y)

    return new_y


## MAIN SCRIPT ##
if __name__ == '__main__':
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))
    ax1.set_title('User & Driver Acquisition Costs vs. Lyft\'s Take')
    ax2.set_title('Revenue, Cost, & Profit vs. Lyft\'s Take')
    ax1.set_xlabel('Lyft\'s Take')
    ax1.set_ylabel('$')
    ax2.set_xlabel('Lyft\'s Take')
    ax2.set_ylabel('$')
    ax1.set_xlim(-0.5, 15.5)
    ax1.set_ylim(0, 3500)
    ax2.set_xlim(-0.5, 15.5)
    ax2.set_ylim(-4000, 4000)

    # numpy array for all possible fees by lyft
    lyft_take_array = np.linspace(0,15.0,1500)

    #----------------------------------#
    ## MONTHLY PROFIT

    # calculating match rate for each of those fees
    match_rate_array = positive_match_from_lyft_take_linear(lyft_take_array)
    
    # calculating profit array for profit from each of those fees and match rates
    profit_array = initial_num_users * match_rate_array * lyft_take_array
    ax2.plot(lyft_take_array, profit_array, color='green', label='Profit')
    
    #----------------------------------#
    ## MONTHLY COST
    # calculating fail rate from match rate array
    fail_rate_array = 1.0 - match_rate_array

    # calculating number of users lost given fail rate and match rate
    users_lost_array = initial_num_users*(match_rate_array*rider_success_match_churn + fail_rate_array*rider_failed_match_churn)

    # calculating number of drivers lost in a given month
    drivers_lost_array = np.full(1500, initial_num_drivers * driver_churn)

    # calculating user acquisition costs from number of users lost
    user_acquisition_cost = calculate_user_acquisition_cost(users_lost_array)
    ax1.plot(lyft_take_array, user_acquisition_cost, color='blue', label='User Cost')

    # calculating driver acquisition costs
    driver_acquisition_cost = calculate_driver_acquisition_cost(drivers_lost_array)
    ax1.plot(lyft_take_array, driver_acquisition_cost, color='orange', label='Driver Cost')

    # calculating monthly costs
    cost_array = user_acquisition_cost + driver_acquisition_cost
    ax2.plot(lyft_take_array, cost_array, color='red', label='Cost')

    #----------------------------------#
    ## MONTHLY REVENUE
    # calculating monthly revenue
    revenue_array = profit_array - cost_array
    ax2.plot(lyft_take_array, revenue_array, color='blue', label='Revenue')

    # calculating max revenue point
    max_revenue = (lyft_take_array[revenue_array.argmax()], revenue_array.max())
    ax2.plot(max_revenue[0], max_revenue[1], 'o')
    ax2.annotate(f'Max Revenue @ ${round_to_nearest_cent(max_revenue[0])}',
                xy=(max_revenue[0], revenue_array.max()),
                xytext=(10, 1), textcoords='offset pixels', fontsize=10)
    
    # final plotting
    ax1.legend()
    ax2.legend()
    fig.subplots_adjust(hspace=0.5)
    plt.show()


    

