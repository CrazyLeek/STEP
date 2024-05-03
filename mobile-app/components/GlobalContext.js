
import React, {useState, useRef} from "react";

export const GlobalContext = React.createContext();

export const GlobalContextProvider = ({ children }) => {
    const [selectedJourney, setSelectedjourney] = useState([]);
    const [newTripAdded, setNewTripAdded] = useState(false);
    const refSelectedTrip = useRef(selectedJourney);
  
    return (
      <GlobalContext.Provider 
        value={{
            selectedJourney, setSelectedjourney, refSelectedTrip, 
            newTripAdded, setNewTripAdded
        }}
      >
        {children}
      </GlobalContext.Provider>
    );
  };


const SelectedJourney = () => {

    let selectedJourney = [];

    return {
      get: () => selectedJourney,
      set: (newValue) => selectedJourney = newValue,
    }
}

export const selectedJourneyFromGlobal = SelectedJourney();