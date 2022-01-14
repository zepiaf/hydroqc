Values
======

.. toctree::
   :maxdepth: 4

TODO: Describe the meaning of the values returned by the module.

* General

Value name containing the _ts suffix are unix timestamp. Other timestamp will follow the format set in the configuration.

* state
  The values underneath this topic represent the current state of the various items at the time winter_credit.py was run.

 * **current_period**
   The current period type

    * normal
    * anchor
    * peak
  
 * **current_period_time_of_day**
   The current period combined to the general time of day

    * anchor_morning
    * anchor_evening
    * peak_morning
    * peak_evening
    * normal

 * **current_composite_state**
   The current combined period and critical status

   * normal_normal
   * normal_critical
   * anchor_morning_normal
   * anchor_morning_critical
   * anchor_evening_normal
   * anchor_evening_critical
   * peak_morning_normal
   * peak_morning_critical
   * peak_evening_normal
   * peak_evening_critical

 * **critical**
   Whether the next peak period is critical or not. This value is used in the current_composite_state

   * true
   * false
 
 * **event_in_progress**
   Whether we are currently in a critical peak event (current_period = peak and critical = true)
   
   * true
   * false

 * **pre_heat**
   If we are currently in a configured pre-heat event

   * true
   * false

 * **upcoming_event**
   Is there a current Hydro-Quebec announcement for an event. Will be true as soon as winter_credit.py sees an annoucement by HQ.

   * true
   * false

 * **morning_event_today & evening_event_today**
   Will be true if there is a critical peak period during the specific time of current day.

   * true
   * false
 * **morning_event_tomorrow & evening_event_tomorrow**
   Will be true if there is a critical peak period during the specific time of the day tomorrow.

   * true
   * false
  

* next
  The topics underneath this topic represent the next various periods.
  * critical
  * anchor
  * peak

  Each of the above will have the following values (except critical which may be absent if no upcoming critical peak event is in the future)
  * start
  * end
  * start_ts
  * end_ts
  * critical (true|false)




* today
  The values under this topic represent the periods during the current day (0h00-23h59).
  * anchor_periods

   * morning
   * evening
  
  * peak_periods

   * morning
   * evening

  Each of the above will have the following values (except critical which may be absent if no upcoming critical peak event is in the future)
  * start
  * end
  * start_ts
  * end_ts