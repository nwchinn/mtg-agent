# MTG Collection Agent

An AI-powered assistant for Magic: The Gathering collection management, analysis, and deck building consultation. This application provides card inventory tracking, financial valuation, and deck recommendations based on ownership analysis.

## Setup

### Prerequisites

- Python 3.8+
- Git
- OpenAI API access

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/mtg-agent.git
cd mtg-agent
python -m venv venv

# Activate virtual environment - note you will need to do this every time you open a new terminal but no need to install them every time
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Execution

```bash
# Launch application
python collection_agent.py
```

## Usage Examples

The agent can respond to natural language queries such as:

- "Query cards from the Outlaws of Thunder Junction set in my collection"
- "Calculate the total market value of my collection"
- "List all legendary creatures in my inventory"
- "Identify Commander decks with high ownership percentage"
- "Filter cards with market value exceeding $10"

## Custom Collection Integration (Optional)

The application includes sample collection data for immediate use without requiring personal data.

To integrate with your personal collection:

### ManaBox Export Procedure:

1. Launch the ManaBox mobile application
2. Navigate to the Collection interface
3. Access the contextual menu (⋮) in the upper right corner
4. Select the "Export to CSV" option
5. Transfer the resulting file to your development environment
6. Place the exported file in the following directory structure:

```
mtg-agent/
  └── data/
      └── ManaBox_Collection.csv
```

## Technical Architecture

### Technology Stack
- Python 3.8+
- OpenAI API integration
- ManaBox data parsing and normalization
- Multi-agent architecture with specialized domain knowledge

### Repository Structure
- `requirements.txt`: Dependency specifications
- `collection_agent.py`: Application entry point
- `tools/`: Collection analysis utilities
- `models/`: Data structures and type definitions

### API Authentication

Create an environment variable configuration file (named: `.env`) in the project root containing your OpenAI API credentials:

```
OPENAI_API_KEY=your-api-key
```

or in each terminal session run:

```
export OPENAI_API_KEY=your-api-key
```

## Advanced Capabilities [WIP]

- Temporal analysis of card valuation trends
- Algorithmically generated deck recommendations based on collection overlap
- Price data integration with TCGPlayer and Scryfall APIs
- Commander deck construction optimization

## Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [ManaBox Developer Information](https://manabox.app/)
- [Scryfall API Documentation](https://scryfall.com/docs/api)

---