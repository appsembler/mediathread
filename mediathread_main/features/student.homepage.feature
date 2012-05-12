Feature: Homepage

    Scenario: 1. Empty Student Homepage
        Using selenium
        Given I am logged in as test_student_one
        Give I am in the Sample Course class
        When I access the url "/"
        Then I am at the Home page
        Then there is not an Instructor Dashboard button
        There is not a FROM YOUR INSTRUCTOR column
        There is an ANALYSIS column
        There is help for the ANALYSIS column
        There is a Compositions column
        There is a Collections column
        There is help for the Compositions column
        There is help for the Collections column
        Finished using Selenium