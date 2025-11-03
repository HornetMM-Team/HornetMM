local NAME = "Your Project Name" -- Required
local ATH = "Author Name" --Optional
local DESC = "Your Description" -- Required
local VER = "Your Current Version" -- Optional
local APIVER = "Your HKMAPI Version" -- Required
local Image = "Optional Image"

-- Import the hmm module (provided by Python loader)
local hmm = require("hmm")

features = {"foo", "boo", "hollow knight"} --Optional Feature table

function hmm.info()
    hmm.setname(NAME)
    hmm.setathour(ATH)
    hmm.setdescription(DESC)
    hmm.setversion(VER) -- Pass the version parameter
end

function hmm.extfeatures()
    -- Add Features from features with only specific values
    -- Loop through features and add each one
    for i, feature in ipairs(features) do
        hmm.addextfeaturevalue(feature)
    end
    
    -- Or add all features at once
    hmm.addextfeature(features)
end