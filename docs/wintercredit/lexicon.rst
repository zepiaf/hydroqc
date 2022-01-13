Lexicon
=======

.. toctree::
   :maxdepth: 4

The following are the terms in use in this module and coming as much as
possible from the official Hydro-Quebec electricy rates document (page
31) :

https://www.hydroquebec.com/data/documents-donnees/pdf/electricity-rates.pdf

and from the “Régie de l’énergie” document :

http://publicsde.regie-energie.qc.ca/projets/469/DocPrj/R-4057-2018-B-0062-DDR-RepDDR-2018_10_26.pdf#page=124

**Period**
    A period is time window where a specific billing or algorythmic logic is
    applied by HQ. It can be of any of the following types:

        * normal
            A period when nothing special is defined by HQ rate policies

        * peak
            In this module:
                All hours from 06:00 to 09:00 and from 16:00 to 20:00 during the winter.

            This is when the critical peak events from hydro are happening.

            In hydro’s document there are also exclusions for specific holiday dates (Christmas, New year, Good Friday
            and Easter Monday) that we don’t take into account here (yet)

        * critical
            When a period is critical it can means two things depending on the period:

                **peak period** + **ongoing critical peak event**

                The current peak period is part of a “critical peak event”

                **normal period or anchor period** + **upcomming critical peak event**

                Means that the next immediate peak period will be a “critical peak event”


        * anchor
            This period starts 5 hours before the next peak event’s start time and has a duration of 3 hours. With the
            current peak period (as described above) it results in the following time periods:

                **Morning** 01h00-04h00

                **Evening** 11h00-14h00

            This period is used by HQ in combination with the reference period to calculate the Reference Energy used to
            calculate the credit by trying to guess the additionnal energy usage caused by the colder temperature.

            In HQ’s rate document it is called temperature adjustment and in the “Regie de l’énergie” document it is
            refered to as an “anchor” period.

        * pre-heat
            A period of time when we want to run some automations before a critical peak event’s start.

            Ex: raise the thermostat setpoint.

**Event**
    An event is also referred to a “critical peak event” means that HQ sent a
    notification that the peak period will be considered critical and
    admissible to winter credits.

**reference period**
    This value is not used or provided in winter_module.py but is good
    to know about to give some context to the calculations.

    The period corresponding to the last 5 non-critical event, differentiated by weekend vs week days.

    **Examples:**

    Saturday evening critical peak event’s reference period = Last 5
    non-critical evening peaks that occurred on weekend days

    Wednesday morning critical peak event’s reference period = Last 5
    non-critical morning peaks that occurred on week days


