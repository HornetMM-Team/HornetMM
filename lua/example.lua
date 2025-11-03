local NAME = "Your Project Name" -- Required
local ATH = "Author Name" --Optional
local DESC = "Your Description" -- Required
local VER = "Your Current Version" -- Optional
local APIVER = "Your HKMAPI Version" -- Required
local Image = "Optional Image"


features = {"foo, "boo", "hollowknight"} --Optional Feature table

 function hmm.info()
    hmm.setname(NAME)
    hmm.setathour(ATH)
    hmm.setdescription(DESC)
    hmm.setversion()
  end
  function hmm.extfeatures()
    -- Add Features from features with only specific values
    hmm.addextfeaturevalue(feature = features[])
    hmm.addextfeature(manualfeature=features)
  end



  
