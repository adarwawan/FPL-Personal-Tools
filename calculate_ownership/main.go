package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"sync"
)

const (
	CURRENT_GAMEWEEK = 7
)

type Pick struct {
	Element       int  `json:"element"`
	Position      int  `json:"position"`
	IsCaptain     bool `json:"is_captain"`
	IsViceCaptain bool `json:"is_vice_captain"`
	Multiplier    int  `json:"multiplier"`
}

type ManagerPicks struct {
	Picks []Pick `json:"picks"`
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func worker(id int, data []int, wg *sync.WaitGroup) (map[int]int, error) {
	gameweek := CURRENT_GAMEWEEK
	isPlayOnly := false
	isCaptain := false
	ownership := make(map[int]int)
	defer wg.Done()
	for _, value := range data {
		picks, err := getManagerPicks(value, gameweek)
		if err != nil {
			fmt.Println("Error:", err)
			return ownership, err
		}

		for _, pick := range picks.Picks {

			multiplier := pick.Multiplier
			if !isCaptain {
				multiplier = min(multiplier, 1)
			}

			if !isPlayOnly {
				multiplier = max(multiplier, 1)
			}

			ownership[pick.Element] += multiplier

		}
	}

	return ownership, nil
}

func getManagerPicks(managerID int, gameweek int) (*ManagerPicks, error) {
	url := fmt.Sprintf("https://fantasy.premierleague.com/api/entry/%d/event/%d/picks/", managerID, gameweek)

	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("failed to fetch data: %s", resp.Status)
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var managerPicks ManagerPicks
	if err := json.Unmarshal(body, &managerPicks); err != nil {
		return nil, err
	}

	return &managerPicks, nil
}

func readTopManager(filename string) ([]int, error) {
	var numbers []int
	var err error

	// Open the file
	file, err := os.Open(filename)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return numbers, err
	}
	defer file.Close()

	// Initialize a slice to hold the integers

	// Use bufio.Scanner to read the file line by line
	scanner := bufio.NewScanner(file)

	for scanner.Scan() {
		// Convert the string line to an integer
		num, err := strconv.Atoi(scanner.Text())
		if err != nil {
			fmt.Println("Error converting to integer:", err)
			return numbers, err
		}

		// Append the integer to the slice
		numbers = append(numbers, num)
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("Error reading file:", err)
	}
	return numbers, err
}

func main() {
	workers := 50

	managerIDs, err := readTopManager("../top_manager.txt")
	if err != nil {
		fmt.Println("Error:", err)
	}

	sliceSize := len(managerIDs) / workers
	pools := make([]map[int]int, 0)

	var wg sync.WaitGroup
	var mu sync.Mutex
	wg.Add(workers)

	for i := 0; i < workers; i++ {
		// Determine the start and end indices for this worker
		start := i * sliceSize
		end := start + sliceSize
		if i == workers-1 {
			end = len(managerIDs) // Ensure the last worker picks up any remaining elements
		}

		// Launch a worker goroutine
		go func(n int, start int, end int, managerIDs []int) {
			fmt.Println(start, end, n)
			data := managerIDs[start:end]
			a, _ := worker(n, data, &wg)

			mu.Lock()
			pools = append(pools, a)
			mu.Unlock()
		}(i, start, end, managerIDs)
	}

	// Wait for all workers to finish
	wg.Wait()

	finalPool := make(map[int]int)

	for _, pool := range pools {
		for k, v := range pool {
			finalPool[k] += v
		}
	}

	writeMap(finalPool)
}

func writeMap(myMap map[int]int) {
	file, err := os.Create("../output.txt")
	if err != nil {
		fmt.Println("Error creating file:", err)
		return
	}
	defer file.Close()

	// Iterate over the map and write each key-value pair to the file
	for key, value := range myMap {
		// Write formatted string to the file
		_, err := fmt.Fprintf(file, "%d: %d\n", key, value)
		if err != nil {
			fmt.Println("Error writing to file:", err)
			return
		}
	}

	fmt.Println("Map data written to file successfully.")
}
